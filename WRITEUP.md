# Write-up

## What I built

A conversational grant advisor for Singapore businesses with a hybrid decision flow:

- fast rule-based clarification for vague/borderline inputs,
- BM25 retrieval for relevant grants,
- LLM-generated recommendations,
- deterministic server-side guardrails that enforce eligibility and citation correctness before any recommendation is returned.

The system now prefers asking one targeted follow-up question over returning recommendations that cannot be confidently validated.

## Architecture

```
User message
  → Query Analyzer (rule-based)
      VAGUE      → Clarifier question + options (no LLM)
      BORDERLINE → Clarifier question + options (no LLM)
      CLEAR      → ConversationProfile Extractor
                 → Retriever (BM25, top-k)
                 → Pre-LLM Eligibility Check (missing signal?)
                     YES → Clarifier question + options
                     NO  → Context Compressor
                         → Prompt Builder
                         → LLM Driver (primary + fallback)
                         → Validator (JSON/schema)
                         → EligibilityGuard (deterministic enforcement)
                             eligible recs exist    → Response
                             none but missing signal→ Clarifier question
                             none and no signal     → Generic clarification
```

## Key engineering decisions and hardening

### 1) Deterministic eligibility and citation enforcement

I added a strict `EligibilityGuard` after model output parsing.

For each recommended grant, the backend now verifies:

- grant `id` exists in `grants.json`,
- every `cited` key exists on that grant,
- every `cited` value matches the dataset value,
- eligibility constraints pass against extracted profile signals:
  - `employee_count_min` / `employee_count_max`
  - `requires_local_entity`
  - `requires_new_market`
  - `applicant_type`
  - `revenue_band`

Recommendations that fail these checks are dropped. If nothing eligible remains, the system asks one targeted follow-up question instead of returning potentially wrong output.

Tradeoff: this is stricter and can increase clarification turns, but it improves trust and auditability.

### 2) Conversation profile extraction

I added a deterministic `ConversationProfile` extractor across user history + latest message with fields:

- `employee_count`
- `local_entity`
- `new_market`
- `applicant_type`
- `revenue_band`

This allows the system to validate grants without relying on the model to be perfectly consistent.

Tradeoff: extraction is heuristic (regex + phrase logic), so unusual phrasing may still require extra clarification.

### 3) Clarification strategy improvements

Clarifier questions/options now cover additional missing eligibility signals:

- new market status
- applicant type (`sme` vs `non_sme`)
- revenue band (`under_100m` vs `over_100m`)

Questions are prioritized so one answer should maximally improve eligibility resolution.

### 4) Runtime resilience with driver fallback

I kept the `LLMDriver` interface but hardened execution:

- `ClaudeCLIDriver` now has timeout control and classified failures:
  - `timeout`
  - `command_missing`
  - `non_zero_exit`
- Added env-driven driver factory.
- Added Codex CLI fallback driver and single-attempt fallback flow.

Default behavior:

- primary: `claude_cli`
- fallback: `codex_cli`

Tradeoff: fallback adds complexity but prevents complete failure when local CLI path is unavailable.

### 5) API safety

I replaced raw exception passthrough with a sanitized stable error response for `/api/chat` while logging internal details server-side.

### 6) Frontend reliability and UX stability

I added moderate UX/reliability hardening:

- request sequencing guard to prevent stale responses from overwriting newer state,
- disabled quick-reply chips and `New` while a request is in-flight,
- inline retry for failed sends,
- `aria-live`/status improvements and clearer labels,
- focus retention for input after pending completes,
- env-based API base URL (`NEXT_PUBLIC_API_BASE_URL`, default localhost).

## Config and interfaces

Public API shape is unchanged:

- `POST /api/chat` still returns either:
  - `{ type: "question", question, options? }`
  - `{ type: "recommendation", grants, tradeoffs? }`
- `DELETE /api/session/{session_id}` unchanged
- `GET /api/grants` unchanged

Backend env vars:

- `LLM_PROVIDER` (default `claude_cli`)
- `LLM_TIMEOUT_SECONDS` (default `45`)
- `LLM_FALLBACK_PROVIDER` (default `codex_cli`)
- `CODEX_MODEL` (optional; used when `codex_cli` is selected)

Frontend env var:

- `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`)

## Testing

I expanded backend coverage for the new hardening layer:

- profile extraction behavior and negation handling,
- eligibility pass/fail matrix and citation matching,
- fallback driver behavior (primary success, fallback path, both-fail path),
- driver factory env behavior,
- API error sanitization,
- matcher flow updates for strict guardrails.

Current backend status:

- `92 passed` (`pytest -q`)

I could not execute frontend lint/build in this environment because Node/NPM are not installed.

## Clarifying questions I didn't ask

The brief was intentionally lightweight. Here are the questions I could have raised and the assumptions I made instead:

**What does a correct recommendation look like?**
I assumed "correct" means: the business is provably eligible based on what they've told us, and every stated reason maps directly to a field in `grants.json`. I built the EligibilityGuard around this definition. An alternative interpretation — surface best-effort matches and let the user self-filter — would have led to a simpler system with no guard layer.

**Should the system handle businesses outside Singapore?**
I assumed Singapore-registered entities only, since every grant in the dataset requires `requires_local_entity: true`. I ask about Singapore registration as a clarifying question but don't hard-block non-local businesses — I leave that to the LLM's reasoning and the EligibilityGuard's enforcement.

**What's the acceptable latency for a response?**
I assumed that a 5–15 second wait for LLM-backed responses is acceptable given the conversational context. This directly informed the decision to use the Claude CLI subprocess rather than building streaming — streaming would have been the right call if the answer were "under 3 seconds, always".

**Should recommendations be ranked by fit or by grant size?**
I assumed fit quality is the right primary sort. The dataset doesn't include funding quanta, so this was partly forced by the data shape, but I would have clarified this in a real engagement.

**Recall vs precision: when in doubt, show more or show fewer?**
I opted for precision — the EligibilityGuard drops unverifiable recommendations rather than surfacing them. This means more clarification turns in some paths. The alternative (show everything, label confidence) would have been a different product call. I flagged this as a question for reviewers rather than assuming an answer.

## Scope decisions

What was deliberately left out, and why:

- **No auth or persistent sessions.** In-memory keyed by UUID is proportionate for an assignment. Adding Redis or a database would have shifted the submission toward infra work rather than product reasoning.
- **No observability stack.** Structured traces, metrics, and alerting are important in production but would have added significant scope with no benefit to a reviewer evaluating the submission.
- **No grant application links or CTAs.** The dataset has no `application_url` field. Adding mock links would have been pure polish with no signal value.
- **Desktop-first layout only.** The Stitch design is mobile-first by spec but the grant advisor use case (detailed business description, multi-turn) maps more naturally to desktop. I didn't build a mobile-optimised layout.
- **No multi-language support.** All keyword heuristics and prompt instructions are English-only. A real Singapore deployment would need to consider Mandarin at minimum.

## Tool use

This submission was developed with the assistance of Claude Code (Anthropic's CLI). All architectural decisions, tradeoffs, module boundaries, and the write-up are my own. I can explain any part of the codebase and the reasoning behind it.

## Assumptions

- In-memory sessions are acceptable for assignment scope.
- BM25 (`k=5`) is sufficient at this dataset size.
- Strict correctness is preferred over maximizing immediate recommendation count.
- No persistence/auth/observability stack was added to keep scope proportional.

## Questions for reviewers

1. When strict eligibility filtering removes all model recommendations, do you prefer:
   - always asking one clarifying question (current behavior), or
   - showing a “best-effort” section clearly labeled as unverified?

2. Should `applicant_type` and `revenue_band` remain required for recommendation confidence, or be treated as optional until explicitly needed by a candidate grant?

3. Is Codex CLI fallback acceptable for your environment, or should fallback stay within the same model vendor family?

4. For assignment evaluation, do you prefer this strict safety posture even if it adds an extra clarification turn in some paths?

5. If you were taking this to production first, would your priority be:
   - persistent sessions,
   - improved profile extraction (NER/classifier), or
   - richer observability (structured traces/metrics)?

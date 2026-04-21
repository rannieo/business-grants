# Write-up

## What I built

A conversational grant advisor. The user describes their business in natural language across multiple turns; the system responds with either a clarifying question or a structured set of grant recommendations with citations.

The primary demo path: a 12-person Singapore software company expanding overseas to Malaysia receives MRA (Market Readiness Assistance) at high fit, with the `requires_new_market` field cited as the reason. A follow-up message about building a new product surfaces EDG-NPD alongside it.

## Architecture

```
User message
  → Query Analyzer (rule-based, NO LLM)
      VAGUE      → Clarifier (template response, NO LLM)
      BORDERLINE → Clarifier (targeted question, NO LLM)
      CLEAR      → Retriever (keyword scoring, top-k)
                   → Context Compressor (strip redundant fields)
                   → Prompt Builder
                   → LLM Driver (Claude CLI subprocess)
                   → Validator (JSON parsing + schema check, retry once)
                   → Response
```

The Query Analyzer gate is the most deliberate design choice. For a grant advisor, many opening messages are too vague to be worth sending to an LLM — "hi", "what grants are available", "we're a startup". Handling these with a rule-based classifier keeps those turns near-instant and costs nothing. Only messages with both a business goal signal and a business context signal reach the LLM.

## LLM driver pattern

There is no hardcoded LLM API call. The `LLMDriver` abstract base class has a single method: `complete(prompt) -> str`. The concrete `ClaudeCLIDriver` shells out to `claude -p` via a subprocess. Any future driver (Anthropic API, OpenAI, local model) implements the same interface and can be swapped at the `app.py` construction site.

The CLI approach was chosen because no API key is required for this submission. The tradeoff is subprocess startup latency (~1–2s) on top of model inference time.

## Explainability

Every recommendation includes a `cited` block that maps specific field names from `grants.json` to the values that drove the recommendation. The LLM is instructed to never invent grant details not present in the data. This is enforced at the prompt level and verified by the Validator, which rejects responses missing the `cited` field.

## Retrieval

Top-k retrieval uses keyword overlap between the full conversation text and each grant's `business_goals` and `supports` fields. Business goals score 3 points per match; supports keywords score 1 point per word match. This is fast, deterministic, and debuggable — no embedding infra required.

The tradeoff: semantic similarity is not captured. A user saying "we want to go global" won't match `overseas_expansion` as reliably as "expand overseas". This is acceptable at this scale (8 grants); at hundreds of grants, embedding-based retrieval would be the right call.

## Grants dataset

Used as-is. The `supports` field is stripped before prompting (redundant with `business_goals`, which is more structured). No other transformations.

## Session state

Conversation history is stored in-memory keyed by a `session_id` UUID generated client-side. Sessions are lost on server restart. For a production system this would move to Redis or a database; for this assignment in-memory is the appropriate scope.

## Open questions

- **Threshold tuning**: The VAGUE / BORDERLINE / CLEAR heuristics use word count and keyword presence. The thresholds (e.g. word count < 6 → VAGUE) were set by inspection against the test cases, not by measuring against a labelled dataset. A real deployment would want a confusion matrix across real user messages.
- **Multi-turn grant filtering**: Currently all grants are re-retrieved on every turn. A more precise approach would carry forward eligibility constraints learned in earlier turns (e.g. once we know the company has 12 employees, filter out grants with `employee_count_min > 12` before retrieval).
- **Validation depth**: The Validator checks JSON structure and required fields but does not verify that cited field values actually match the grants data. A stricter validator would cross-reference citations against the dataset.
- **Session persistence**: Should a user be able to return to a previous conversation? The current architecture makes this a straightforward addition (persist `_sessions` to a store), but the product decision is unresolved.

## The task

Build a small application that allows a user to enter a business profile and receive relevant grant recommendations.

A simplified grant dataset is included in this repository for use in the assignment. You may interpret, transform, or extend it if useful, but please explain any meaningful changes.

## Scope

Your solution should include:

- a web UI
- a backend service

## Submission

Please complete the assignment in a private repository and grant reviewer access using the contact details provided in our email, or provide equivalent access on your chosen platform when you are ready for review.

Please also include:

- instructions for running the project locally
- a short write-up covering your assumptions, open questions, and tradeoffs

## Guidance

Treat this like a real piece of engineering work, while keeping the scope proportionate to the assignment.

Your submission should be straightforward for another engineer to run, review, and reason about.

A thoughtful, well-scoped solution is better than a broad one.

We are not looking for maximum feature count or polish for its own sake.

---

## Running locally

**Requirements:** Python 3.11+, Node 18+, [Claude Code CLI](https://claude.ai/code) and [Codex CLI](https://github.com/openai/codex) installed/authenticated (`claude` and `codex` available on your PATH).

### One-command local run

```bash
make serve
```

This starts both apps together (backend on `:8000`, frontend on `:3000`).

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Optional backend environment variables (copy `backend/.env.example` to `backend/.env` to override):

- `LLM_PROVIDER` (default: `claude_cli`)
- `LLM_TIMEOUT_SECONDS` (default: `45`)
- `LLM_FALLBACK_PROVIDER` (default: `codex_cli`)
- `CODEX_MODEL` (optional; used when `codex_cli` is selected)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Optional frontend environment variable (copy `frontend/.env.example` to `frontend/.env` to override):

- `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000`)

Open [http://localhost:3000](http://localhost:3000). The backend must be running at port 8000.

---

## Write-up

Assumptions, architecture decisions, tradeoffs, and open questions are in [WRITEUP.md](WRITEUP.md).

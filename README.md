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

**Requirements:** Python 3.11+, Node 18+, [Claude Code CLI](https://claude.ai/code) installed and authenticated (`claude` available on your PATH).

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The backend must be running at port 8000.

---

## Write-up

Assumptions, architecture decisions, tradeoffs, and open questions are in [WRITEUP.md](WRITEUP.md).

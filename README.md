# Resume/Job Matcher v2 — Batch Explainable Ranking

An explainable candidate-to-job matching agent over synthetic sample data.
This is a demo/learning project, not connected to any real ATS, resume
database, or candidate PII.

## What's new in v2

The original `resume-job-matcher` scored one candidate against one job with a
"why this fits" rationale. This v2 takes a different angle:

- **Batch, many-to-many ranking**: rank every candidate against a job
  (`/rank-candidates`), or every job against a candidate (`/rank-jobs`), in
  one call — the shape a recruiter or job-seeker tool actually needs.
- **Per-criterion breakdown**: every result reports separate skills /
  experience / education sub-scores (weighted 60/25/15) instead of one opaque
  number.
- **Explicit skill-gap output**: each result lists `missing_required_skills`
  and `bonus_skills` (nice-to-have matches), so the rationale is actionable,
  not just descriptive.

## Why this is relevant

Candidate-to-job matching is a common recruiting-tech AI application pattern,
and "explainability" (why did the model rank this way?) is one of the more
practically important trends in applied AI right now — a bare relevance score
is far less useful than a transparent, auditable breakdown a human can check
and challenge.

## Project structure

```
app/
  scoring.py   # weighted rubric: skills / experience / education, fully explainable
  matcher.py   # batch many-to-many ranking over the sample pools
  main.py      # FastAPI app (GET /candidates, GET /jobs, POST /rank-candidates, POST /rank-jobs)
  cli.py       # command-line interface, no server needed
data/          # synthetic sample candidates and job postings
tests/         # pytest suite covering scoring, matching, and the API
```

## Setup

```bash
pip install -r requirements.txt
```

## Run — CLI

```bash
python -m app.cli rank-candidates j1 --top-k 3
python -m app.cli rank-jobs c3 --top-k 2
```

## Run — API server

```bash
uvicorn app.main:app --reload
```

```bash
curl -X POST http://127.0.0.1:8000/rank-candidates \
  -H "Content-Type: application/json" \
  -d '{"job_id": "j1", "top_k": 3}'
```

## Run with Docker

```bash
docker build -t resume-job-matcher-v2 .
docker run -p 8000:8000 resume-job-matcher-v2
```

## Tests

```bash
pytest -v
```

## Disclaimer

This is a demo/simulation project built entirely on synthetic sample
candidates and job postings. It is not a hiring decision tool, is not
connected to any real applicant tracking system, and should not be used to
make real employment decisions.

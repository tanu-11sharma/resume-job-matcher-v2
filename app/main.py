"""FastAPI app exposing batch candidate<->job ranking with explainable scores."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.matcher import JobMatcher

app = FastAPI(
    title="Resume/Job Matcher v2 — Batch Explainable Ranking",
    description="Many-to-many candidate<->job matching over synthetic sample data, "
    "with a weighted, explainable scoring breakdown and skill-gap analysis per result. "
    "Demo project — not connected to any real ATS or candidate data.",
    version="2.0.0",
)

_matcher = JobMatcher()


class RankCandidatesRequest(BaseModel):
    job_id: str
    top_k: int = 5


class RankJobsRequest(BaseModel):
    candidate_id: str
    top_k: int = 5


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "candidates_loaded": len(_matcher.candidates),
        "jobs_loaded": len(_matcher.jobs),
    }


@app.get("/candidates")
def list_candidates() -> list[dict]:
    return _matcher.candidates


@app.get("/jobs")
def list_jobs() -> list[dict]:
    return _matcher.jobs


@app.post("/rank-candidates")
def rank_candidates(payload: RankCandidatesRequest) -> dict:
    try:
        return _matcher.rank_candidates_for_job(payload.job_id, top_k=payload.top_k)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/rank-jobs")
def rank_jobs(payload: RankJobsRequest) -> dict:
    try:
        return _matcher.rank_jobs_for_candidate(payload.candidate_id, top_k=payload.top_k)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

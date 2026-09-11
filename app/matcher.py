"""Batch many-to-many matching over the candidate/job pools with explainable rationale."""
from __future__ import annotations

import json
from pathlib import Path

from app.scoring import score_candidate_against_job

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_candidates() -> list[dict]:
    return json.loads((DATA_DIR / "candidates.json").read_text())


def load_jobs() -> list[dict]:
    return json.loads((DATA_DIR / "jobs.json").read_text())


class JobMatcher:
    def __init__(self, candidates: list[dict] | None = None, jobs: list[dict] | None = None):
        self.candidates = candidates if candidates is not None else load_candidates()
        self.jobs = jobs if jobs is not None else load_jobs()
        self._candidates_by_id = {c["id"]: c for c in self.candidates}
        self._jobs_by_id = {j["id"]: j for j in self.jobs}

    def rank_candidates_for_job(self, job_id: str, top_k: int = 5) -> dict:
        job = self._jobs_by_id.get(job_id)
        if job is None:
            raise KeyError(f"Unknown job_id: {job_id}")

        ranked = []
        for candidate in self.candidates:
            breakdown = score_candidate_against_job(candidate, job)
            ranked.append(
                {
                    "candidate_id": candidate["id"],
                    "candidate_name": candidate["name"],
                    **breakdown.to_dict(),
                }
            )
        ranked.sort(key=lambda r: r["overall_score"], reverse=True)

        return {"job_id": job_id, "job_title": job["title"], "ranked_candidates": ranked[:top_k]}

    def rank_jobs_for_candidate(self, candidate_id: str, top_k: int = 5) -> dict:
        candidate = self._candidates_by_id.get(candidate_id)
        if candidate is None:
            raise KeyError(f"Unknown candidate_id: {candidate_id}")

        ranked = []
        for job in self.jobs:
            breakdown = score_candidate_against_job(candidate, job)
            ranked.append({"job_id": job["id"], "job_title": job["title"], **breakdown.to_dict()})
        ranked.sort(key=lambda r: r["overall_score"], reverse=True)

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate["name"],
            "ranked_jobs": ranked[:top_k],
        }

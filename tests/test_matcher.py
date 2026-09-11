import pytest

from app.matcher import JobMatcher, load_candidates, load_jobs


def test_sample_data_loads():
    assert len(load_candidates()) >= 4
    assert len(load_jobs()) >= 3


def test_rank_candidates_for_job_is_sorted_descending():
    matcher = JobMatcher()
    result = matcher.rank_candidates_for_job("j1", top_k=10)
    scores = [c["overall_score"] for c in result["ranked_candidates"]]
    assert scores == sorted(scores, reverse=True)


def test_rank_candidates_for_job_respects_top_k():
    matcher = JobMatcher()
    result = matcher.rank_candidates_for_job("j1", top_k=2)
    assert len(result["ranked_candidates"]) == 2


def test_rank_candidates_unknown_job_raises():
    matcher = JobMatcher()
    with pytest.raises(KeyError):
        matcher.rank_candidates_for_job("does-not-exist")


def test_rank_jobs_for_candidate_is_sorted_descending():
    matcher = JobMatcher()
    result = matcher.rank_jobs_for_candidate("c1", top_k=10)
    scores = [j["overall_score"] for j in result["ranked_jobs"]]
    assert scores == sorted(scores, reverse=True)


def test_rank_jobs_unknown_candidate_raises():
    matcher = JobMatcher()
    with pytest.raises(KeyError):
        matcher.rank_jobs_for_candidate("does-not-exist")


def test_ml_candidate_best_fits_ml_job():
    matcher = JobMatcher()
    result = matcher.rank_jobs_for_candidate("c3", top_k=1)  # Priya Nair: ML background
    assert result["ranked_jobs"][0]["job_id"] == "j3"

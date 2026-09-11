from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["candidates_loaded"] >= 4
    assert body["jobs_loaded"] >= 3


def test_list_candidates_and_jobs():
    assert client.get("/candidates").status_code == 200
    assert client.get("/jobs").status_code == 200


def test_rank_candidates_endpoint():
    resp = client.post("/rank-candidates", json={"job_id": "j1", "top_k": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["ranked_candidates"]) == 3
    assert "missing_required_skills" in body["ranked_candidates"][0]


def test_rank_candidates_endpoint_404_on_unknown_job():
    resp = client.post("/rank-candidates", json={"job_id": "nope"})
    assert resp.status_code == 404


def test_rank_jobs_endpoint():
    resp = client.post("/rank-jobs", json={"candidate_id": "c1"})
    assert resp.status_code == 200
    assert "ranked_jobs" in resp.json()

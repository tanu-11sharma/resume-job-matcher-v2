from app.scoring import score_candidate_against_job

JOB = {
    "id": "j1",
    "title": "Backend Engineer (Python)",
    "min_years_experience": 3,
    "min_education_level": "bachelors",
    "required_skills": ["python", "fastapi", "postgresql", "docker"],
    "nice_to_have_skills": ["aws", "kubernetes"],
}


def test_strong_match_scores_high():
    candidate = {
        "id": "c1",
        "name": "Ava",
        "years_experience": 4,
        "education_level": "bachelors",
        "skills": ["python", "fastapi", "postgresql", "docker", "aws"],
    }
    result = score_candidate_against_job(candidate, JOB)
    assert result.overall_score > 0.85
    assert result.missing_required_skills == []
    assert "aws" in result.bonus_skills


def test_missing_required_skills_are_reported():
    candidate = {
        "id": "c2",
        "name": "Marco",
        "years_experience": 1,
        "education_level": "bachelors",
        "skills": ["javascript", "react"],
    }
    result = score_candidate_against_job(candidate, JOB)
    assert set(result.missing_required_skills) == {"python", "fastapi", "postgresql", "docker"}
    assert result.overall_score < 0.4


def test_experience_below_bar_gets_partial_credit_not_zero():
    candidate = {
        "id": "c3",
        "name": "New Grad",
        "years_experience": 1,
        "education_level": "bachelors",
        "skills": ["python", "fastapi", "postgresql", "docker"],
    }
    result = score_candidate_against_job(candidate, JOB)
    assert 0 < result.experience_score < 1.0


def test_education_below_requirement_scores_partial():
    candidate = {
        "id": "c4",
        "name": "Self Taught",
        "years_experience": 5,
        "education_level": "highschool",
        "skills": ["python", "fastapi", "postgresql", "docker"],
    }
    job_masters = {**JOB, "min_education_level": "masters"}
    result = score_candidate_against_job(candidate, job_masters)
    assert result.education_score < 1.0


def test_score_is_bounded_between_0_and_1():
    candidate = {
        "id": "c5",
        "name": "Overqualified",
        "years_experience": 20,
        "education_level": "phd",
        "skills": ["python", "fastapi", "postgresql", "docker", "aws", "kubernetes"],
    }
    result = score_candidate_against_job(candidate, JOB)
    assert 0.0 <= result.overall_score <= 1.0

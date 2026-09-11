"""
Explainable, weighted-rubric scoring engine for candidate <-> job matching.

v2 twist vs. the original resume-job-matcher: instead of a single one-to-one
score, this module exposes a per-criterion breakdown (skills / experience /
education) plus an explicit skill-gap list, so it can power batch many-to-many
ranking (see matcher.py) with the "why this fits" rationale attached to every
result rather than a single pairing.
"""
from __future__ import annotations

from dataclasses import dataclass, field

EDUCATION_RANK = {"highschool": 0, "associates": 1, "bachelors": 2, "masters": 3, "phd": 4}

# Weights are intentionally simple and documented, not learned, so the score
# is fully explainable end to end.
WEIGHTS = {"skills": 0.6, "experience": 0.25, "education": 0.15}


@dataclass
class MatchBreakdown:
    overall_score: float
    skills_score: float
    experience_score: float
    education_score: float
    matched_skills: list[str] = field(default_factory=list)
    missing_required_skills: list[str] = field(default_factory=list)
    bonus_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "overall_score": self.overall_score,
            "breakdown": {
                "skills_score": self.skills_score,
                "experience_score": self.experience_score,
                "education_score": self.education_score,
            },
            "matched_skills": self.matched_skills,
            "missing_required_skills": self.missing_required_skills,
            "bonus_skills": self.bonus_skills,
        }


def _skills_score(candidate_skills: set[str], job: dict) -> tuple[float, list, list, list]:
    required = {s.lower() for s in job.get("required_skills", [])}
    nice_to_have = {s.lower() for s in job.get("nice_to_have_skills", [])}
    candidate_skills = {s.lower() for s in candidate_skills}

    matched_required = candidate_skills & required
    missing_required = required - candidate_skills
    matched_nice = candidate_skills & nice_to_have

    if not required:
        base = 1.0
    else:
        base = len(matched_required) / len(required)

    # Nice-to-have skills add a capped bonus so they can't outweigh required skills.
    bonus = min(0.15, 0.05 * len(matched_nice))
    score = min(1.0, base + bonus)

    matched_all = sorted(matched_required | matched_nice)
    return score, matched_all, sorted(missing_required), sorted(matched_nice)


def _experience_score(years: float, min_years: float) -> float:
    if min_years <= 0:
        return 1.0
    if years >= min_years:
        # Small bonus for exceeding the bar, capped at 1.0.
        return min(1.0, 0.85 + 0.05 * min(3, years - min_years))
    # Partial credit that decays the further below the bar the candidate is.
    return max(0.0, years / min_years) * 0.7


def _education_score(candidate_level: str, min_level: str) -> float:
    c_rank = EDUCATION_RANK.get(candidate_level.lower(), 0)
    m_rank = EDUCATION_RANK.get(min_level.lower(), 0)
    if c_rank >= m_rank:
        return 1.0
    if m_rank == 0:
        return 1.0
    return max(0.0, c_rank / m_rank)


def score_candidate_against_job(candidate: dict, job: dict) -> MatchBreakdown:
    skills_score, matched, missing, bonus = _skills_score(set(candidate["skills"]), job)
    experience_score = _experience_score(
        candidate["years_experience"], job.get("min_years_experience", 0)
    )
    education_score = _education_score(
        candidate["education_level"], job.get("min_education_level", "highschool")
    )

    overall = (
        WEIGHTS["skills"] * skills_score
        + WEIGHTS["experience"] * experience_score
        + WEIGHTS["education"] * education_score
    )

    return MatchBreakdown(
        overall_score=round(overall, 4),
        skills_score=round(skills_score, 4),
        experience_score=round(experience_score, 4),
        education_score=round(education_score, 4),
        matched_skills=matched,
        missing_required_skills=missing,
        bonus_skills=bonus,
    )

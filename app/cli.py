"""CLI: rank candidates for a job, or jobs for a candidate, without running a server."""
from __future__ import annotations

import argparse
import json

from app.matcher import JobMatcher


def main() -> None:
    parser = argparse.ArgumentParser(description="Resume/Job Matcher v2 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("rank-candidates", help="Rank candidates for a job")
    p1.add_argument("job_id")
    p1.add_argument("--top-k", type=int, default=5)

    p2 = sub.add_parser("rank-jobs", help="Rank jobs for a candidate")
    p2.add_argument("candidate_id")
    p2.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    matcher = JobMatcher()

    if args.command == "rank-candidates":
        result = matcher.rank_candidates_for_job(args.job_id, top_k=args.top_k)
    else:
        result = matcher.rank_jobs_for_candidate(args.candidate_id, top_k=args.top_k)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

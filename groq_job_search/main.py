import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from groq_job_search.job_search import (
    search_all,
    save_raw_jobs
)

from groq_job_search.job_ranker import JobRanker

from groq_job_search.report import (
    generate_markdown
)


load_dotenv()

sys.stdout.reconfigure(
    encoding="utf-8"
)


def print_header():
    print()
    print("=" * 70)
    print("                 GROQ AI JOB SEARCH")
    print("=" * 70)
    print()


def print_job_result(index, result):

    job = result["job"]
    analysis = result["analysis"]

    print()
    print("-" * 70)

    print(
        f"{index}. {job.get('title')}"
    )

    print(
        f"   Company : {job.get('company')}"
    )

    print(
        f"   Location: {job.get('location')}"
    )

    print(
        f"   Source  : {job.get('source')}"
    )

    print(
        f"   Match   : {analysis.get('match_score')}%"
    )

    print(
        f"   Fit     : {analysis.get('fit_level')}"
    )

    print(
        f"   Priority: {analysis.get('application_priority')}"
    )

    print()

    print(
        "   Matching skills:"
    )

    for skill in analysis.get(
        "matching_skills", []
    ):
        print(f"      + {skill}")

    print()

    print(
        "   Missing / gap:"
    )

    gaps = (
        analysis.get("hard_requirement_gaps", [])
        + analysis.get("missing_skills", [])
    )

    if gaps:
        for gap in gaps[:8]:
            print(f"      - {gap}")
    else:
        print("      None identified")

    print()

    summary = analysis.get("summary")

    if summary:
        print(
            f"   Summary: {summary}"
        )

    print()

    print(
        f"   URL: {job.get('url')}"
    )


def main():

    parser = argparse.ArgumentParser(
        description="Groq-powered AI job search"
    )

    parser.add_argument(
        "--query",
        default="Python Automation Software Engineer"
    )

    parser.add_argument(
        "--location",
        default="India"
    )

    parser.add_argument(
        "--country",
        default="IN"
    )

    parser.add_argument(
        "--job-age",
        type=int,
        default=14
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5
    )

    args = parser.parse_args()

    print_header()

    print(
        f"Query      : {args.query}"
    )

    print(
        f"Location   : {args.location}"
    )

    print(
        f"Job age    : {args.job_age} days"
    )

    print(
        f"Portal limit: {args.limit}"
    )

    print()

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    print("[1/4] Searching job portals...")
    print()

    try:
        jobs = search_all(
            query=args.query,
            linkedin_location=args.location,
            country=args.country,
            job_age=args.job_age,
            limit=args.limit
        )

    except Exception as exc:

        print()
        print("ERROR DURING JOB SEARCH")
        print(exc)

        sys.exit(1)

    print()
    print(
        f"Found {len(jobs)} unique jobs."
    )

    if not jobs:
        print(
            "No jobs found."
        )
        sys.exit(0)

    # --------------------------------------------------
    # SAVE RAW
    # --------------------------------------------------

    save_raw_jobs(jobs)

    # --------------------------------------------------
    # GROQ ANALYSIS
    # --------------------------------------------------

    print()
    print("[2/4] Loading Groq job matcher...")

    try:
        ranker = JobRanker()

    except Exception as exc:

        print()
        print("ERROR INITIALIZING GROQ")
        print(exc)

        sys.exit(1)

    results = []

    print()
    print("[3/4] Analyzing jobs with Groq...")
    print()

    for index, job in enumerate(jobs, 1):

        print(
            f"  [{index}/{len(jobs)}] "
            f"{job.get('title')} "
            f"— {job.get('company')}"
        )

        try:

            analysis = ranker.rank_job(job)

            results.append({
                "job": job,
                "analysis": analysis
            })

            print(
                f"       Match: "
                f"{analysis.get('match_score')}% "
                f"| {analysis.get('fit_level')}"
            )

        except Exception as exc:

            print(
                f"       ERROR: {exc}"
            )

            results.append({
                "job": job,
                "analysis": {
                    "match_score": 0,
                    "fit_level": "low",
                    "application_priority": "low_priority",
                    "summary": (
                        "Groq analysis failed. "
                        "Review manually."
                    ),
                    "key_risks": [
                        str(exc)
                    ]
                }
            })

    # --------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------

    json_path = Path(
        "groq_job_search/output/job_results.json"
    )

    json_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with json_path.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False
        )

    # --------------------------------------------------
    # REPORT
    # --------------------------------------------------

    print()
    print("[4/4] Generating report...")

    report_path = generate_markdown(
        results
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print()
    print_header()

    print(
        "JOB MATCH RESULTS"
    )

    for index, result in enumerate(
        sorted(
            results,
            key=lambda x: x["analysis"].get(
                "match_score", 0
            ),
            reverse=True
        ),
        1
    ):

        print_job_result(
            index,
            result
        )

    print()
    print("=" * 70)

    print(
        f"JSON report : {json_path}"
    )

    print(
        f"Markdown    : {report_path}"
    )

    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_command(command: list[str]) -> str:
    process = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if process.returncode != 0:
        raise RuntimeError(
            f"Command failed:\n"
            f"{' '.join(command)}\n\n"
            f"STDOUT:\n{process.stdout}\n\n"
            f"STDERR:\n{process.stderr}"
        )

    return process.stdout


def parse_json_output(raw: str) -> dict:
    raw = raw.strip()

    start = raw.find("{")

    if start == -1:
        raise ValueError(
            "Could not find JSON object in CLI output."
        )

    return json.loads(raw[start:])


# def fetch_linkedin_detail(job_id: str) -> dict:
#     """Fetch full LinkedIn job details using the job ID."""
#     if not job_id:
#         return {}

#     cli = (
#         ROOT
#         / ".agents"
#         / "skills"
#         / "linkedin-search"
#         / "cli"
#         / "src"
#         / "cli.ts"
#     )

#     command = [
#         "bun",
#         "run",
#         str(cli),
#         "detail",
#         job_id,
#         "--format",
#         "json",
#     ]

#     try:
#         raw = run_command(command)
#         return parse_json_output(raw)
#     except Exception as exc:
#         print(f"    Warning: Could not fetch LinkedIn detail for {job_id}: {exc}")
#         return {}



def fetch_linkedin_detail(job_id: str) -> dict:
    """Fetch full LinkedIn job details using the job ID."""
    if not job_id:
        return {}

    cli = (
        ROOT
        / ".agents"
        / "skills"
        / "linkedin-search"
        / "cli"
        / "src"
        / "cli.ts"
    )

    command = [
        "bun",
        "run",
        str(cli),
        "detail",
        job_id,
        "--format",
        "json",
    ]

    try:
        raw = run_command(command)
        return parse_json_output(raw)
    except Exception as exc:
        print(
            f"    Warning: Could not fetch LinkedIn detail "
            f"for {job_id}: {exc}"
        )
        return {}







# def search_linkedin(
#     query: str,
#     location: str = "India",
#     job_age: int = 14,
#     limit: int = 10
# ) -> list[dict]:

#     cli = ROOT / ".agents" / "skills" / "linkedin-search" / "cli" / "src" / "cli.ts"

#     command = [
#         "bun",
#         "run",
#         str(cli),
#         "search",
#         "--location",
#         location,
#         "--query",
#         query,
#         "--jobage",
#         str(job_age),
#         "--limit",
#         str(limit),
#         "--format",
#         "json"
#     ]

#     print("  Searching LinkedIn...")

#     raw = run_command(command)
#     data = parse_json_output(raw)

#     results = []

#     for job in data.get("results", []):
#         results.append({
#             "id": str(job.get("id", "")),
#             "title": job.get("title", ""),
#             "company": job.get("company", ""),
#             "location": job.get("location", ""),
#             "date": job.get("date", ""),
#             "url": job.get("url", ""),
#             "description": job.get("description", ""),
#             "source": "LinkedIn",
#             "work_mode": job.get("work_mode")
#         })

#     return results


def search_linkedin(
    query: str,
    location: str = "India",
    job_age: int = 14,
    limit: int = 10
) -> list[dict]:

    cli = (
        ROOT
        / ".agents"
        / "skills"
        / "linkedin-search"
        / "cli"
        / "src"
        / "cli.ts"
    )

    command = [
        "bun",
        "run",
        str(cli),
        "search",
        "--location",
        location,
        "--query",
        query,
        "--jobage",
        str(job_age),
        "--limit",
        str(limit),
        "--format",
        "json"
    ]

    print("  Searching LinkedIn...")

    raw = run_command(command)
    data = parse_json_output(raw)

    results = []

    for job in data.get("results", []):
        job_id = str(job.get("id", ""))

        # Search results may not contain the full description.
        detail = fetch_linkedin_detail(job_id)

        # Detail response may use different field names depending
        # on the CLI response structure.
        description = (
            detail.get("description")
            or detail.get("jobDescription")
            or job.get("description")
            or ""
        )

        results.append({
            "id": job_id,
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "date": job.get("date", ""),
            "url": job.get("url", ""),
            "description": description,
            "source": "LinkedIn",
            "work_mode": (
                job.get("work_mode")
                or detail.get("work_mode")
                or detail.get("workMode")
            )
        })

    return results



def search_linkedin(
    query: str,
    location: str = "India",
    job_age: int = 14,
    limit: int = 10
) -> list[dict]:

    cli = (
        ROOT
        / ".agents"
        / "skills"
        / "linkedin-search"
        / "cli"
        / "src"
        / "cli.ts"
    )

    command = [
        "bun",
        "run",
        str(cli),
        "search",
        "--location",
        location,
        "--query",
        query,
        "--jobage",
        str(job_age),
        "--limit",
        str(limit),
        "--format",
        "json"
    ]

    print("  Searching LinkedIn...")

    raw = run_command(command)
    data = parse_json_output(raw)

    results = []

    for job in data.get("results", []):
        job_id = str(job.get("id", ""))

        print(f"    Fetching details: {job_id}")

        detail = fetch_linkedin_detail(job_id)

        description = (
            detail.get("description")
            or job.get("description")
            or ""
        )

        results.append({
            "id": job_id,
            "title": detail.get("title") or job.get("title", ""),
            "company": detail.get("company") or job.get("company", ""),
            "location": detail.get("location") or job.get("location", ""),
            "date": detail.get("date") or job.get("date", ""),
            "url": detail.get("url") or job.get("url", ""),
            "description": description,
            "source": "LinkedIn",
            "work_mode": (
                job.get("work_mode")
                or detail.get("work_mode")
                or detail.get("workMode")
            ),
            "seniority": detail.get("seniority"),
            "employment_type": detail.get("employmentType"),
            "job_function": detail.get("jobFunction"),
            "industries": detail.get("industries"),
            "is_active": detail.get("isActive"),
        })

    return results









def search_freehire(
    query: str,
    country: str = "IN",
    job_age: int = 14,
    limit: int = 10
) -> list[dict]:

    cli = ROOT / ".agents" / "skills" / "freehire-search" / "cli" / "src" / "cli.ts"

    command = [
        "bun",
        "run",
        str(cli),
        "search",
        "--query",
        query,
        "--country",
        country,
        "--jobage",
        str(job_age),
        "--limit",
        str(limit),
        "--format",
        "json"
    ]

    print("  Searching FreeHire...")

    raw = run_command(command)
    data = parse_json_output(raw)

    results = []

    for job in data.get("results", []):
        results.append({
            "id": str(job.get("id", "")),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "date": job.get("date", ""),
            "url": job.get("url", ""),
            "description": job.get("description", ""),
            "source": "FreeHire",
            "work_mode": job.get("work_mode"),
            "skills": job.get("skills", [])
        })

    return results


def normalize_text(value: str) -> str:
    return " ".join(
        (value or "").lower().strip().split()
    )


def job_key(job: dict) -> str:
    url = normalize_text(job.get("url", ""))

    if url:
        return url

    company = normalize_text(job.get("company", ""))
    title = normalize_text(job.get("title", ""))

    return f"{company}|{title}"


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    unique = {}

    for job in jobs:
        key = job_key(job)

        if key not in unique:
            unique[key] = job

    return list(unique.values())


def search_all(
    query: str = "Python Automation Software Engineer",
    linkedin_location: str = "India",
    country: str = "IN",
    job_age: int = 14,
    limit: int = 10
) -> list[dict]:

    linkedin_jobs = search_linkedin(
        query=query,
        location=linkedin_location,
        job_age=job_age,
        limit=limit
    )

    freehire_jobs = search_freehire(
        query=query,
        country=country,
        job_age=job_age,
        limit=limit
    )

    combined = linkedin_jobs + freehire_jobs

    unique = deduplicate_jobs(combined)

    return unique


def save_raw_jobs(jobs: list[dict], path="groq_job_search/data/jobs.json"):
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(jobs),
        "jobs": jobs
    }

    with output.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
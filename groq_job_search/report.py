from pathlib import Path
from datetime import datetime


def safe(value):
    if value is None:
        return ""

    return str(value)


def generate_markdown(
    results: list[dict],
    output_path="groq_job_search/output/job_report.md"
):

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    results = sorted(
        results,
        key=lambda x: x.get("analysis", {}).get(
            "match_score", 0
        ),
        reverse=True
    )

    lines = []

    lines.append("# AI Job Search Report")
    lines.append("")
    lines.append(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    lines.append("")
    lines.append(
        f"Jobs analyzed: **{len(results)}**"
    )
    lines.append("")

    for index, item in enumerate(results, 1):

        job = item.get("job", {})
        analysis = item.get("analysis", {})

        title = safe(job.get("title"))
        company = safe(job.get("company"))
        location = safe(job.get("location"))
        url = safe(job.get("url"))
        source = safe(job.get("source"))

        score = analysis.get("match_score", 0)
        fit = safe(analysis.get("fit_level"))
        priority = safe(
            analysis.get("application_priority")
        )

        lines.append(
            f"## {index}. {title}"
        )

        lines.append("")
        lines.append(
            f"**Company:** {company}"
        )
        lines.append(
            f"**Location:** {location}"
        )
        lines.append(
            f"**Source:** {source}"
        )
        lines.append(
            f"**Match:** {score}%"
        )
        lines.append(
            f"**Fit:** {fit}"
        )
        lines.append(
            f"**Priority:** {priority}"
        )

        if url:
            lines.append(
                f"**Job:** {url}"
            )

        lines.append("")

        summary = analysis.get("summary")

        if summary:
            lines.append(
                f"**Summary:** {summary}"
            )
            lines.append("")

        lines.append("### Matching Skills")

        for skill in analysis.get(
            "matching_skills", []
        ):
            lines.append(f"- {skill}")

        lines.append("")

        lines.append("### Transferable Skills")

        for skill in analysis.get(
            "transferable_skills", []
        ):
            lines.append(f"- {skill}")

        lines.append("")

        lines.append("### Missing Skills")

        for skill in analysis.get(
            "missing_skills", []
        ):
            lines.append(f"- {skill}")

        lines.append("")

        lines.append("### Hard Requirements")

        for requirement in analysis.get(
            "hard_requirements", []
        ):
            lines.append(f"- {requirement}")

        lines.append("")

        lines.append("### Hard Requirement Gaps")

        for gap in analysis.get(
            "hard_requirement_gaps", []
        ):
            lines.append(f"- {gap}")

        lines.append("")

        lines.append("### Why It Matches")

        for reason in analysis.get(
            "why_it_matches", []
        ):
            lines.append(f"- {reason}")

        lines.append("")

        lines.append("### Why It May Not Match")

        for reason in analysis.get(
            "why_it_may_not_match", []
        ):
            lines.append(f"- {reason}")

        lines.append("")

        lines.append("### Risks")

        for risk in analysis.get(
            "key_risks", []
        ):
            lines.append(f"- {risk}")

        lines.append("")
        lines.append("---")
        lines.append("")

    output.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return output
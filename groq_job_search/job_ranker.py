import json
import re
from pathlib import Path

# from .groq_job_search.llm import GroqLLM
from .llm import GroqLLM
from .profile import PROFILE


class JobRanker:

    def __init__(self):
        self.llm = GroqLLM()

        prompt_path = (
            Path(__file__).resolve().parent
            / "prompts"
            / "rank.txt"
        )

        self.system_prompt = prompt_path.read_text(
            encoding="utf-8"
        )

    @staticmethod
    def extract_json(text: str) -> dict:
        text = text.strip()

        if text.startswith("```"):
            text = re.sub(
                r"^```(?:json)?\s*",
                "",
                text,
                flags=re.IGNORECASE
            )

            text = re.sub(
                r"\s*```$",
                "",
                text
            )

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                f"Groq did not return JSON:\n{text}"
            )

        return json.loads(
            text[start:end + 1]
        )

    def rank_job(self, job: dict) -> dict:

        job_text = {
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "date": job.get("date"),
            "work_mode": job.get("work_mode"),
            "skills": job.get("skills", []),
            "description": job.get("description", "")
        }

        user_prompt = f"""
CANDIDATE PROFILE:

{PROFILE.to_prompt_text()}

JOB:

{json.dumps(job_text, indent=2, ensure_ascii=False)}

Analyze the job against the candidate.
"""

        response = self.llm.generate(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt,
            temperature=0.1
        )

        return self.extract_json(response)
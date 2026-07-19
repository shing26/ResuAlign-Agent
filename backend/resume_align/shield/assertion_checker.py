"""Assertion Checker: anti-hallucination guard that validates no fabricated skills appear."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Common tech keywords to check
TECH_KEYWORDS: set[str] = {
    "python", "java", "javascript", "typescript", "go", "golang", "rust",
    "c++", "c#", "kotlin", "swift", "ruby", "php", "scala", "perl",
    "react", "vue", "angular", "svelte", "next.js", "nuxt.js",
    "node.js", "deno", "express", "django", "flask", "spring", "fastapi",
    "kubernetes", "k8s", "docker", "terraform", "ansible", "helm",
    "aws", "gcp", "azure", "cloudflare", "alicloud",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "kafka", "rabbitmq", "nats", "pulsar",
    "pytorch", "tensorflow", "langchain", "pydantic",
    "grpc", "graphql", "rest", "websocket",
    "ci/cd", "jenkins", "github actions", "gitlab ci",
    "prometheus", "grafana", "datadog", "opentelemetry",
}


class AssertionChecker:
    """Checks tailored output for fabricated tech entities."""

    def __init__(self, custom_tech_set: set[str] | None = None) -> None:
        self.tech_set = custom_tech_set or TECH_KEYWORDS

    def extract_tech_entities(self, text: str) -> set[str]:
        """Extract known tech entities from text (case-insensitive)."""
        found: set[str] = set()
        text_lower = text.lower()
        for keyword in self.tech_set:
            pattern = re.compile(r"\b" + re.escape(keyword) + r"\b", re.IGNORECASE)
            if pattern.search(text_lower):
                found.add(keyword)
        return found

    def check(
        self,
        tailored_text: str,
        original_skills: set[str],
        jd_skills: set[str],
    ) -> dict[str, Any]:
        """Assert that tailored output contains no fabricated entities.

        Returns:
            Dict with:
            - passed: bool
            - original_skills_found: set
            - jd_skills_found: set
            - fabricated_skills: set (entities found in output but not in original or JD)
            - missing_jd_skills: set (JD skills not found in output)
        """
        output_skills = self.extract_tech_entities(tailored_text)
        original_normalized = {s.lower() for s in original_skills}
        jd_normalized = {s.lower() for s in jd_skills}
        output_normalized = {s.lower() for s in output_skills}

        fabricated = output_normalized - original_normalized - jd_normalized
        missing = jd_normalized - output_normalized

        result = {
            "passed": len(fabricated) == 0,
            "original_skills_found": sorted(original_normalized & output_normalized),
            "jd_skills_found": sorted(jd_normalized & output_normalized),
            "fabricated_skills": sorted(fabricated),
            "missing_jd_skills": sorted(missing),
        }

        if fabricated:
            logger.warning(
                "Assertion FAILED: fabricated entities detected: %s", fabricated
            )

        return result

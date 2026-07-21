"""Assertion Checker: anti-hallucination guard that validates no fabricated skills appear."""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# Common tech keywords to check
SYNONYM_GROUPS: list[set[str]] = [
    {"docker", "container", "containerization", "containerized"},
    {"kubernetes", "k8s", "orchestration", "container orchestration"},
    {"async", "asynchronous", "non-blocking"},
    {"concurrent", "parallel", "multi-threaded", "high concurrency", "high throughput"},
    {"resilient", "fault-tolerant", "high availability", "ha", "failover"},
    {"scalable", "scalability", "horizontal scaling", "auto-scaling"},
    {"monitoring", "observability", "telemetry", "metrics", "prometheus", "grafana"},
    {"caching", "cache", "redis", "memcached"},
    {"ci/cd", "continuous integration", "continuous deployment", "automated deployment"},
    {"microservices", "service-oriented", "microservice architecture"},
    {"cloud", "cloud-native", "cloud computing", "aws", "gcp", "azure"},
    {"real-time", "realtime", "live", "streaming"},
    {"distributed", "distributed system", "distributed architecture"},
    {"api", "rest api", "restful", "graphql", "grpc"},
    {"messaging", "message queue", "kafka", "rabbitmq", "pub/sub"},
    {"database", "db", "data store", "sql", "nosql"},
    {"monolith", "monolithic", "single service"},
]
SYNONYM_MAP: dict[str, set[str]] = {}
for group in SYNONYM_GROUPS:
    for term in group:
        SYNONYM_MAP.setdefault(term, set()).update(group)

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

        raw_fabricated = output_normalized - original_normalized - jd_normalized
        synonym_matched = set()
        truly_fabricated = set()
        for term in raw_fabricated:
            is_synonym = any(known in SYNONYM_MAP.get(term, set()) for known in (original_normalized | jd_normalized))
            if is_synonym:
                synonym_matched.add(term)
            else:
                truly_fabricated.add(term)
        missing = jd_normalized - output_normalized

        result = {
            "passed": len(truly_fabricated) == 0,
            "original_skills_found": sorted(original_normalized & output_normalized),
            "jd_skills_found": sorted(jd_normalized & output_normalized),
            "fabricated_skills": sorted(truly_fabricated),
            "synonym_matched": sorted(synonym_matched),
            "missing_jd_skills": sorted(missing),
        }

        if truly_fabricated:
            logger.warning(
                "Assertion FAILED: fabricated entities detected: %s", truly_fabricated
            )

        return result

    COMMON_ACTION_WORDS: set = {
    "主导", "负责", "优化", "重构", "设计", "构建", "提升", "实现",
    "降低", "支撑", "迭代", "集成", "封装", "推进", "部署", "搭建"
}

def _extract_tech_entities(self, text: str) -> set:
    if not text:
        return set()
    import re
    pattern = r"[a-zA-Z0-9\+\#\.\-]+"
    matches = re.findall(pattern, text)
    return {m.upper() for m in matches if len(m) > 1 and not m.isdigit()}

def verify_diff_delta(self, diff_delta: DiffDelta, base_resume: ResumeContext) -> DiffDelta:
    base_entities = self._extract_tech_entities(base_resume.raw_text)
    for item in diff_delta.diff_items:
        proposed = self._extract_tech_entities(item.proposed_text)
        original = self._extract_tech_entities(item.original_text or "")
        newly = proposed - original
        hallucinated = []
        for e in newly:
            if e not in base_entities and e.lower() not in self.COMMON_ACTION_WORDS:
                if e not in base_resume.raw_text.upper():
                    hallucinated.append(e)
        if hallucinated:
            item.confidence = ConfidenceLevel.LOW
            item.reason += f" | Hallucination alert: {chr(44).join(hallucinated)}"
    return diff_delta

def _is_synonym(self, term, known_set):
        for known in known_set:
            if term in SYNONYM_MAP.get(known, set()):
                return True
            if known in SYNONYM_MAP.get(term, set()):
                return True
        return False

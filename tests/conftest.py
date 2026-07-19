"""Shared test fixtures."""
from __future__ import annotations

import pytest


@pytest.fixture
def sample_resume_text() -> str:
    return """# Professional Summary
Senior backend engineer with 5 years of experience in Python and distributed systems.

# Technical Skills
- Languages: Python, Java, TypeScript
- Frameworks: FastAPI, Spring Boot, React
- Databases: PostgreSQL, Redis, MongoDB
- Tools: Docker, Kubernetes, Git, CI/CD

# Work Experience

## Senior Backend Engineer | TechCorp | 2021-Present
- Designed and implemented a high-throughput payment system handling 10k+ TPS
- Reduced API latency by 40% through Redis caching and query optimization
- Led migration from monolith to microservices architecture (12 services)
- Maintained 99.99% uptime for critical payment infrastructure

## Backend Developer | StartupX | 2019-2021
- Built RESTful APIs serving 100k+ daily active users
- Implemented real-time notification system using WebSocket and Kafka
- Reduced deployment time by 60% with Docker and GitHub Actions CI/CD

# Education
- M.S. in Computer Science, University X (2017-2019)
- B.S. in Software Engineering, University Y (2013-2017)
"""


@pytest.fixture
def sample_jd_text() -> str:
    return """Senior Backend Engineer - ByteDance

Responsibilities:
- Design and develop high-performance distributed systems
- Optimize system throughput and latency under high concurrency
- Collaborate with product teams to deliver scalable solutions

Requirements:
- 5+ years of experience in backend development
- Strong proficiency in Python or Go
- Deep understanding of distributed systems and microservices
- Experience with Redis, Kafka, or similar middleware
- Familiar with Kubernetes and cloud-native technologies

Preferred:
- Experience with large-scale recommendation systems
- Knowledge of Flink or Spark
"""


@pytest.fixture
def sample_structured_jd() -> dict:
    return {
        "title": "Senior Backend Engineer",
        "company": "ByteDance",
        "required_skills": ["Python", "Go", "Distributed Systems", "Microservices", "Redis", "Kafka", "Kubernetes"],
        "nice_to_have": ["Flink", "Spark", "Recommendation Systems"],
        "responsibilities": ["Design distributed systems", "Optimize throughput and latency"],
        "seniority": "Senior",
    }

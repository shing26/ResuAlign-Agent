"""Resume context model (Pydantic)."""

from pydantic import BaseModel


class ResumeContext(BaseModel):
    raw_text: str = ""

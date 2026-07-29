"""Job context model (Pydantic)."""

from pydantic import BaseModel


class JobContext(BaseModel):
    raw_text: str = ""
    title: str = ""
    company: str = ""

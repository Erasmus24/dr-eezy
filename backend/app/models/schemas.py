from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    profession: Optional[str] = None  # "Doctor" | "Nurse" | None


class ChatSource(BaseModel):
    label: Optional[str] = None
    doc_type: Optional[str] = None


class ChatAction(BaseModel):
    type: str
    url: str
    label: str


class ChatResponse(BaseModel):
    answer: str
    used_local_llm: bool
    sources: List[ChatSource]
    action: Optional[ChatAction] = None


class JobMatch(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = None
    specialty: Optional[str] = None
    profession: Optional[str] = None
    match_score: Optional[float] = None
    description_snippet: Optional[str] = None


class CVUploadResponse(BaseModel):
    candidate_name: Optional[str] = None
    profession: Optional[str] = None
    job_title: Optional[str] = None
    experience_years: int
    skills: List[str]
    registration: Optional[str] = None
    matches: List[JobMatch]


class RosterGenerateRequest(BaseModel):
    start_date: date
    num_days: int = 7
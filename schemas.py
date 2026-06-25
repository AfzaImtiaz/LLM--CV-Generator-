from pydantic import BaseModel, Field
from typing import Literal


class CoverLetterRequest(BaseModel):
    job_title: str = Field(..., max_length=120)
    company_name: str = Field(..., max_length=120)
    job_description: str = Field(..., max_length=4000)
    candidate_background: str = Field(..., max_length=3000)
    tone: Literal["formal", "conversational", "confident"] = "formal"
    language: str = Field(default="English", max_length=50)


class HealthResponse(BaseModel):
    status: str
    model: str
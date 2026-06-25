"""
FastAPI entrypoint. Run with: uvicorn app.main:app --reload
"""
import time
from dotenv import load_dotenv
load_dotenv()
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from app.history import save_entry, get_history
from app.schemas import CoverLetterRequest, HealthResponse
from app.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm_client import stream_cover_letter, MODEL

app = FastAPI(title="Smart Cover Letter Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
)

_request_log: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT = 5
WINDOW_SECONDS = 60


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    recent = [t for t in _request_log[ip] if now - t < WINDOW_SECONDS]
    if len(recent) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Try again shortly.")
    recent.append(now)
    _request_log[ip] = recent


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", model=MODEL)


@app.post("/generate")
def generate(req: CoverLetterRequest, request: Request) -> StreamingResponse:
    _check_rate_limit(request.client.host)
    user_prompt = build_user_prompt(
        job_title=req.job_title,
        company_name=req.company_name,
        job_description=req.job_description,
        candidate_background=req.candidate_background,
        tone=req.tone,
        language=req.language,
    )

    def stream_and_save():
        full_text = ""
        for chunk in stream_cover_letter(SYSTEM_PROMPT, user_prompt):
            full_text += chunk
            yield chunk
        save_entry({
            "job_title": req.job_title,
            "company_name": req.company_name,
            "tone": req.tone,
            "language": req.language,
            "letter": full_text,
        })

    return StreamingResponse(
        stream_and_save(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )

@app.get("/templates")
def templates():
    return [
        {
            "name": "Fresh Graduate — Tech",
            "job_title": "Junior Python Developer",
            "company_name": "Systems Ltd",
            "job_description": "Looking for a Python developer with FastAPI and REST API experience. Knowledge of SQL and Git preferred.",
            "candidate_background": "Final-year CS student at FAST Islamabad. Built 3 projects using Python and FastAPI. Familiar with PostgreSQL and GitHub.",
            "tone": "confident",
            "language": "English"
        },
        {
            "name": "Marketing Role — Mid Level",
            "job_title": "Digital Marketing Executive",
            "company_name": "Unilever Pakistan",
            "job_description": "Seeking a marketing executive with experience in social media, content creation, and campaign analytics.",
            "candidate_background": "2 years experience at a digital agency. Managed Instagram and Facebook campaigns for 5 brands. Increased client engagement by 40%.",
            "tone": "formal",
            "language": "English"
        },
        {
            "name": "Remote Job — International",
            "job_title": "Frontend Developer",
            "company_name": "Remote First Inc",
            "job_description": "Looking for a React developer with TypeScript experience for a fully remote role. Must be comfortable with async communication.",
            "candidate_background": "3 years building React apps. Worked remotely for a UK startup. Strong communication skills and self-managed.",
            "tone": "conversational",
            "language": "English"
        }
        ]      


@app.get("/history")
def history(limit: int = 50):
    return get_history(limit=limit)
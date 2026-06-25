LetterForge

AI-powered cover letter generator — streams a tailored, role-specific cover letter using Google's Gemini API, with multi-language support, generation history, and ready-to-use templates.

---

## Features

- **Streaming generation** — the cover letter appears word-by-word in real time instead of waiting for the full response
- **Tone control** — Confident, Formal, or Conversational
- **Multi-language output** — generate letters in English, Urdu, Arabic, French, and other languages (actively being refined — see [Known Limitations](#known-limitations))
- **Generation history** — every letter generated is saved automatically and browsable from the UI
- **Pre-filled templates** — three example scenarios (fresh graduate, mid-level, remote/international) to fill the form instantly
- **Built-in rate limiting** — a simple in-memory limiter (5 requests/minute per IP) to protect the API key from accidental overuse

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| AI Model | Google Gemini API (`gemini-2.5-flash`) |
| Frontend | HTML, CSS, vanilla JavaScript |
| Storage | JSON file (history) |

---

## Project Structure
coverletter_generator/

├── app/

│   ├── main.py          # FastAPI entrypoint, routes

│   ├── llm_client.py    # Gemini API streaming wrapper

│   ├── prompts.py       # System prompt + prompt construction

│   ├── schemas.py       # Pydantic request/response models

│   └── history.py       # JSON-file-backed history store

├── frontend/

│   └── index.html       # Single-page UI

├── .env                 # API key (not committed)

├── .env.example

├── requirements.txt

└── README.md

---

## Setup

### 1. Clone and create a virtual environment

```bash
python -m venv venv
```

**Windows (PowerShell):**
```powershell
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& ".\venv\Scripts\Activate.ps1")
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API key

```bash
cp .env.example .env
```

Open `.env` and add your key:
GEMINI_API_KEY=your_actual_key_here

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

---

## Running the App

You need **two terminals running at the same time** — one for the backend, one for the frontend. Both must stay open while you use the app.

### Terminal 1 — Backend

From the project root:

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:
INFO: Uvicorn running on http://127.0.0.1:8000

INFO: Application startup complete.

### Terminal 2 — Frontend

```bash
cd frontend
python -m http.server 3002
```

Then open in your browser: **http://localhost:3002/**

> **Note:** If either terminal is closed, that half of the app stops working — restart the relevant command to bring it back.

---

## Testing the API Directly

### Using curl

```bash
curl -N -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Python Developer",
    "company_name": "Systems Ltd",
    "job_description": "Looking for a Python developer with FastAPI experience.",
    "candidate_background": "Final-year CS student, built 3 AI projects.",
    "tone": "confident",
    "language": "English"
  }'
```

### Health check

```bash
curl http://localhost:8000/health
```

### Interactive API docs

**http://localhost:8000/docs**

---

## API Reference

### `POST /generate`

Streams a generated cover letter as plain text.

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `job_title` | string | yes | max 120 chars |
| `company_name` | string | yes | max 120 chars |
| `job_description` | string | yes | max 4000 chars |
| `candidate_background` | string | yes | max 3000 chars |
| `tone` | string | no | `formal` \| `conversational` \| `confident` (default: `formal`) |
| `language` | string | no | e.g. `English`, `Urdu`, `Arabic` (default: `English`) |

**Response:** `text/plain` streamed chunks.

### `GET /history`

Returns the most recent saved cover letters (default limit: 50).

**Query params:** `limit` (optional, integer)

**Response:**

```json
[
  {
    "job_title": "Python Developer",
    "company_name": "Systems Ltd",
    "tone": "confident",
    "language": "English",
    "letter": "Dear Hiring Manager...",
    "timestamp": 1750000000.0
  }
]
```

### `GET /health`

Simple health check. Returns the active model name.

---

## Known Limitations

- **Language generation is a work in progress.** The `language` field and prompt are in place, but the model does not yet switch language with full reliability for every option. This is an active area of improvement, not a finished feature.
- **History is stored in a single local JSON file**, suitable for demo/single-user use. It is not safe for concurrent multi-user production traffic — swap for a real database before any wider deployment.
- **Rate limiting is in-memory and per-process**, not distributed. It resets if the server restarts and won't work correctly across multiple server instances.
- **Gemini free-tier quota is shared and can be inconsistent under load** — occasional 429 errors during heavy testing are expected on the free tier, not a bug.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| "Could not reach the server" | Backend not running | Start `uvicorn` in its own terminal |
| `Could not import module "main"` | Wrong uvicorn command | Use `uvicorn app.main:app`, not `uvicorn main:app` |
| `ERR_INCOMPLETE_CHUNKED_ENCODING` | Outdated `google-genai` SDK | `pip install --upgrade google-genai` |
| `404 NOT_FOUND` on model | Invalid/old model name | Use `gemini-2.5-flash` in `llm_client.py` |
| `429 RESOURCE_EXHAUSTED` | Free-tier rate limit hit | Wait a minute, or reduce test frequency |

---

## License

Built as part of an LLM Bootcamp project. For educational use

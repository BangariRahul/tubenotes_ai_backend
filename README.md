# TubeNotes AI — FastAPI backend

This starter accepts a YouTube video ID, note type, and optional custom instructions; fetches captions; generates structured English notes with LangChain/OpenAI; and returns a formatted PDF directly to the client.

## 1. Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then add your OpenAI API key. Never commit `.env` or expose your API key in the Chrome extension.

## 2. Run locally

```bash
uvicorn main:app --reload
```

- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

## 3. Request

POST `http://127.0.0.1:8000/api/notes`

JSON body:
```json
{
  "video_id": "dQw4w9WgXcQ",
  "note_type": "study",
  "custom_instructions": "Include simple examples and a final revision checklist."
}
```

Allowed `note_type` values: `summary`, `study`, `detailed`, `flashcards`, `action`, `transcript`.

The response is a PDF (`Content-Type: application/pdf`) with an attachment filename. FastAPI returns errors as JSON with a useful HTTP status when input, transcript retrieval, or generation fails.

## 4. Connect from the extension

Use `fetch` with method `POST`, JSON headers, and the request body above. Read the response as a Blob and trigger a download. Add `http://127.0.0.1:8000/*` to the extension's `host_permissions` for local development, and reload the extension after editing the manifest.

## Notes before public deployment

- This is a practical starter, not a complete hardened multi-user service. Add authentication, rate limiting, request/job timeouts, usage limits, monitoring, and deployment secrets management before public release.
- Restrict CORS to the exact origins you need. CORS is not authentication.
- Check YouTube transcript API behavior and applicable terms. Captions may be unavailable or access may be blocked.
- Very long transcripts are truncated at `MAX_TRANSCRIPT_CHARS`; consider token-aware chunking/map-reduce for long videos.
- The transcript library's network calls and LLM calls can be slow. Consider background jobs and task queues for higher traffic.
- Do not log API keys or full transcripts. Keep secrets out of source control.

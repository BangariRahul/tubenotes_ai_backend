import logging
import re
from io import BytesIO
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from config import settings
from schemas import NotesRequest
from summary_generator_service import SummaryGeneratorService
from pdf_service import create_notes_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tubenotes")

app = FastAPI(
    title="TubeNotes AI API",
    version="1.0.0",
    description="Generate structured English notes from YouTube videos.",
)

# Keep this list narrow in production. Chrome extension IDs can be added here
# after publishing. Localhost is useful while developing.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


service = SummaryGeneratorService()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/notes", response_class=StreamingResponse)
def generate_notes(request: NotesRequest):
    """Generate a PDF and return it directly as application/pdf."""
    try:
        notes_markdown = service.generate_notes(
            video_id=request.video_id,
            note_type=request.note_type,
            custom_instructions=request.custom_instructions,
        )
        pdf_bytes = create_notes_pdf(
            notes_markdown=notes_markdown,
            video_id=request.video_id,
            note_type=request.note_type.value,
        )
    except ValueError as exc:
        # Known input/transcript/configuration problems safe to show the client.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to generate notes for video_id=%s", request.video_id)
        raise HTTPException(
            status_code=500,
            detail="Notes could not be generated. Please try again later.",
        ) from exc

    safe_type = re.sub(r"[^a-z0-9-]+", "-", request.note_type.value.lower()).strip("-")
    filename = f"youtube-{safe_type or 'notes'}-{request.video_id}.pdf"
    encoded_filename = quote(filename)
    headers = {
        "Content-Disposition": (
            f"attachment; filename=\"{filename}\"; filename*=UTF-8''{encoded_filename}"
        ),
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    }
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers=headers,
    )

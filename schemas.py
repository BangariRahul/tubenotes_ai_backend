from enum import Enum
from pydantic import BaseModel, Field, field_validator


class NoteType(str, Enum):
    summary = "summary"
    study = "study"
    detailed = "detailed"
    flashcards = "flashcards"
    action = "action"
    transcript = "transcript"


class NotesRequest(BaseModel):
    video_id: str = Field(
        min_length=11,
        max_length=11,
        pattern=r"^[A-Za-z0-9_-]{11}$",
        description="11-character YouTube video ID",
    )
    note_type: NoteType = Field(default=NoteType.summary)
    custom_instructions: str = Field(
        default="",
        max_length=1500,
        description="Optional additional preferences. Output remains in English.",
    )

    @field_validator("custom_instructions")
    @classmethod
    def trim_instructions(cls, value: str) -> str:
        return value.strip()

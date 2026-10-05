import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_transcript_chars: int = int(os.getenv("MAX_TRANSCRIPT_CHARS", "80000"))
    cors_origins: list[str] = None

    def __post_init__(self):
        object.__setattr__(
            self,
            "cors_origins",
            _csv_env(
                "CORS_ORIGINS",
                "http://localhost,http://127.0.0.1",
            ),
        )


settings = Settings()

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BACKEND_DIR / "storage"
INDEX_STORAGE_DIR = STORAGE_DIR / "indexes"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
INDEX_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _default_sqlite_url() -> str:
    db_path = STORAGE_DIR / "novel_agent.db"
    return f"sqlite:///{db_path.as_posix()}"


class Settings(BaseModel):
    app_name: str = "Novel Agent MVP"
    database_url: str = os.getenv("DATABASE_URL", _default_sqlite_url())
    cors_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm_provider: str = os.getenv("LLM_PROVIDER", "auto")
    index_storage_path: Path = INDEX_STORAGE_DIR


settings = Settings()

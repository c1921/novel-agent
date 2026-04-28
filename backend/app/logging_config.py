from __future__ import annotations

import logging
import sys
from contextvars import ContextVar, Token
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import BACKEND_DIR, settings

_request_id: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> Token[str]:
    return _request_id.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    _request_id.reset(token)


def get_request_id() -> str:
    return _request_id.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def _resolve_log_file() -> Path:
    log_file = Path(settings.app_log_file)
    if not log_file.is_absolute():
        log_file = BACKEND_DIR / log_file
    log_file.parent.mkdir(parents=True, exist_ok=True)
    return log_file


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if getattr(root_logger, "_novel_agent_logging_configured", False):
        return

    level = getattr(logging, settings.app_log_level.upper(), logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] [request_id=%(request_id)s] %(message)s"
    )
    request_filter = RequestIdFilter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_filter)
    root_logger.addHandler(console_handler)

    if settings.app_log_to_file:
        file_handler = RotatingFileHandler(
            _resolve_log_file(),
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(request_filter)
        root_logger.addHandler(file_handler)

    root_logger.setLevel(level)
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).setLevel(level)

    root_logger._novel_agent_logging_configured = True  # type: ignore[attr-defined]

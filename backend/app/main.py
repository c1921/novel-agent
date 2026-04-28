import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from app.api import agent, chapters, characters, foreshadowing, outlines, projects, worldbuilding
from app.config import settings
from app.database import init_db
from app.logging_config import configure_logging, reset_request_id, set_request_id

configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_http_request(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid4().hex
    token = set_request_id(request_id)
    started_at = perf_counter()
    try:
        response = await call_next(request)
        duration_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "http.request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        response.headers["x-request-id"] = request_id
        return response
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "http.request_failed method=%s path=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise
    finally:
        reset_request_id(token)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    logger.info(
        "app.startup name=%s database_url=%s log_level=%s log_to_file=%s",
        settings.app_name,
        settings.database_url,
        settings.app_log_level,
        settings.app_log_to_file,
    )


@app.get("/api/health")
def health():
    return {"ok": True}


app.include_router(projects.router)
app.include_router(characters.router)
app.include_router(worldbuilding.router)
app.include_router(outlines.router)
app.include_router(chapters.router)
app.include_router(foreshadowing.router)
app.include_router(agent.router)

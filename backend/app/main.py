from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import agent, chapters, characters, foreshadowing, outlines, projects, worldbuilding
from app.config import settings
from app.database import init_db

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


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

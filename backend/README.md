# Novel Agent MVP Backend

FastAPI backend for the novel-writing Agent MVP.

## Install

```powershell
uv sync
```

## Configure

Copy `.env.example` to `.env`.

Without `OPENAI_API_KEY`, `LLM_PROVIDER=auto` uses the built-in Mock provider so the full workflow still runs locally.

## Run

```powershell
uv run uvicorn app.main:app --reload
```

The app creates SQLite tables automatically on startup. Local runtime files are written under `storage/`.

## Check

```powershell
uv run python -m compileall app
```

Health endpoint:

```text
GET /api/health
```

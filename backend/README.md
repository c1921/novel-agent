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

## Logs

Logs are written to stdout and, by default, to:

```text
storage/logs/app.log
```

Useful environment variables:

```env
APP_LOG_LEVEL=INFO
APP_LOG_TO_FILE=true
APP_LOG_FILE=./storage/logs/app.log
```

LLM logs include provider, model, message count, content lengths and duration. They do not include API keys, full prompts or generated chapter text.

## Check

```powershell
uv run python -m compileall app
```

Health endpoint:

```text
GET /api/health
```

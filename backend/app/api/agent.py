from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.agent.graph import run_draft_phase, run_outline_phase, run_question_phase
from app.agent.nodes import save_chapter_from_state
from app.api.chapters import get_chapter_or_404
from app.api.projects import get_project_or_404
from app.database import get_db
from app.rag.indexer import rebuild_project_index

router = APIRouter(prefix="/api/agent", tags=["agent"])


def get_session_or_404(session_id: str, db: Session) -> models.AgentSession:
    item = db.get(models.AgentSession, session_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent session not found")
    return item


def _save_session(db: Session, item: models.AgentSession, state: schemas.NovelAgentState) -> None:
    item.state_json = dict(state)
    item.next_action = str(state.get("next_action", item.next_action))
    db.commit()
    db.refresh(item)


@router.post("/start-chapter", response_model=schemas.StartChapterResponse)
def start_chapter(payload: schemas.StartChapterRequest, db: Session = Depends(get_db)):
    get_project_or_404(payload.project_id, db)

    if payload.chapter_id is None:
        chapter = crud.create_chapter(
            db,
            payload.project_id,
            schemas.ChapterCreate(
                chapter_number=crud.next_chapter_number(db, payload.project_id),
                title="未命名章节",
                goal=payload.user_goal,
                status="planning",
            ),
        )
    else:
        chapter = get_chapter_or_404(payload.project_id, payload.chapter_id, db)
        chapter.goal = payload.user_goal
        chapter.status = "planning"
        db.commit()
        db.refresh(chapter)

    rebuild_project_index(payload.project_id, db)
    initial_state: schemas.NovelAgentState = {
        "project_id": payload.project_id,
        "chapter_id": chapter.id,
        "user_goal": payload.user_goal,
        "messages": [],
    }
    state = run_question_phase(initial_state, db)
    session_id = uuid4().hex
    agent_session = models.AgentSession(
        id=session_id,
        project_id=payload.project_id,
        chapter_id=chapter.id,
        next_action=state.get("next_action", "answer_plot_questions"),
        state_json=dict(state),
    )
    db.add(agent_session)
    db.commit()

    return schemas.StartChapterResponse(
        session_id=session_id,
        next_action=agent_session.next_action,
        plot_questions=state.get("plot_questions", []),
        auto_decidable=state.get("auto_decidable", []),
    )


@router.post("/answer-questions", response_model=schemas.AnswerQuestionsResponse)
def answer_questions(payload: schemas.AnswerQuestionsRequest, db: Session = Depends(get_db)):
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})
    state["user_answers"] = [answer.model_dump() for answer in payload.answers]
    state = run_outline_phase(state, db)
    _save_session(db, agent_session, state)
    return schemas.AnswerQuestionsResponse(
        next_action=state.get("next_action", "approve_outline"),
        chapter_outline=state.get("chapter_outline", ""),
    )


@router.post("/approve-outline", response_model=schemas.ApproveOutlineResponse)
def approve_outline(payload: schemas.ApproveOutlineRequest, db: Session = Depends(get_db)):
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})

    if not payload.approved:
        state["outline_approved"] = False
        state["outline_revision_instruction"] = payload.revision_instruction
        state = run_outline_phase(state, db)
        _save_session(db, agent_session, state)
        return schemas.ApproveOutlineResponse(
            next_action=state.get("next_action", "approve_outline"),
            chapter_outline=state.get("chapter_outline", ""),
        )

    state["outline_approved"] = True
    state = run_draft_phase(state, db)
    _save_session(db, agent_session, state)
    return schemas.ApproveOutlineResponse(
        next_action=state.get("next_action", "review_draft"),
        draft=state.get("draft", ""),
        polished_draft=state.get("polished_draft", ""),
        consistency_report=state.get("consistency_report"),
    )


@router.post("/save-chapter", response_model=schemas.ChapterRead)
def save_chapter(payload: schemas.SaveChapterRequest, db: Session = Depends(get_db)):
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})
    try:
        chapter = save_chapter_from_state(state, db, payload.use_polished)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    state["next_action"] = "completed"
    _save_session(db, agent_session, state)
    rebuild_project_index(agent_session.project_id, db)
    return chapter

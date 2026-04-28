from __future__ import annotations

import logging
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
logger = logging.getLogger(__name__)


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
    logger.info(
        "agent.start_chapter_start project_id=%s chapter_id=%s user_goal_chars=%s",
        payload.project_id,
        payload.chapter_id,
        len(payload.user_goal),
    )
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
    logger.info(
        "agent.start_chapter_done project_id=%s chapter_id=%s session_id=%s questions=%s auto_decidable=%s next_action=%s",
        payload.project_id,
        chapter.id,
        session_id,
        len(state.get("plot_questions", [])),
        len(state.get("auto_decidable", [])),
        agent_session.next_action,
    )

    return schemas.StartChapterResponse(
        session_id=session_id,
        next_action=agent_session.next_action,
        plot_questions=state.get("plot_questions", []),
        auto_decidable=state.get("auto_decidable", []),
    )


@router.post("/answer-questions", response_model=schemas.AnswerQuestionsResponse)
def answer_questions(payload: schemas.AnswerQuestionsRequest, db: Session = Depends(get_db)):
    logger.info(
        "agent.answer_questions_start session_id=%s answers=%s",
        payload.session_id,
        len(payload.answers),
    )
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})
    state["user_answers"] = [answer.model_dump() for answer in payload.answers]
    state = run_outline_phase(state, db)
    _save_session(db, agent_session, state)
    logger.info(
        "agent.answer_questions_done session_id=%s project_id=%s chapter_id=%s outline_chars=%s next_action=%s",
        payload.session_id,
        agent_session.project_id,
        agent_session.chapter_id,
        len(state.get("chapter_outline", "")),
        state.get("next_action", "approve_outline"),
    )
    return schemas.AnswerQuestionsResponse(
        next_action=state.get("next_action", "approve_outline"),
        chapter_outline=state.get("chapter_outline", ""),
    )


@router.post("/approve-outline", response_model=schemas.ApproveOutlineResponse)
def approve_outline(payload: schemas.ApproveOutlineRequest, db: Session = Depends(get_db)):
    logger.info(
        "agent.approve_outline_start session_id=%s approved=%s revision_chars=%s",
        payload.session_id,
        payload.approved,
        len(payload.revision_instruction),
    )
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})

    if not payload.approved:
        state["outline_approved"] = False
        state["outline_revision_instruction"] = payload.revision_instruction
        state = run_outline_phase(state, db)
        _save_session(db, agent_session, state)
        logger.info(
            "agent.approve_outline_revision_done session_id=%s project_id=%s chapter_id=%s outline_chars=%s next_action=%s",
            payload.session_id,
            agent_session.project_id,
            agent_session.chapter_id,
            len(state.get("chapter_outline", "")),
            state.get("next_action", "approve_outline"),
        )
        return schemas.ApproveOutlineResponse(
            next_action=state.get("next_action", "approve_outline"),
            chapter_outline=state.get("chapter_outline", ""),
        )

    state["outline_approved"] = True
    state = run_draft_phase(state, db)
    _save_session(db, agent_session, state)
    logger.info(
        "agent.approve_outline_done session_id=%s project_id=%s chapter_id=%s draft_chars=%s polished_chars=%s issues=%s next_action=%s",
        payload.session_id,
        agent_session.project_id,
        agent_session.chapter_id,
        len(state.get("draft", "")),
        len(state.get("polished_draft", "")),
        len((state.get("consistency_report") or {}).get("issues", [])),
        state.get("next_action", "review_draft"),
    )
    return schemas.ApproveOutlineResponse(
        next_action=state.get("next_action", "review_draft"),
        draft=state.get("draft", ""),
        polished_draft=state.get("polished_draft", ""),
        consistency_report=state.get("consistency_report"),
    )


@router.post("/save-chapter", response_model=schemas.ChapterRead)
def save_chapter(payload: schemas.SaveChapterRequest, db: Session = Depends(get_db)):
    logger.info(
        "agent.save_chapter_request_start session_id=%s use_polished=%s",
        payload.session_id,
        payload.use_polished,
    )
    agent_session = get_session_or_404(payload.session_id, db)
    state = dict(agent_session.state_json or {})
    try:
        chapter = save_chapter_from_state(state, db, payload.use_polished)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    state["next_action"] = "completed"
    _save_session(db, agent_session, state)
    rebuild_project_index(agent_session.project_id, db)
    logger.info(
        "agent.save_chapter_request_done session_id=%s project_id=%s chapter_id=%s status=%s",
        payload.session_id,
        agent_session.project_id,
        chapter.id,
        chapter.status,
    )
    return chapter

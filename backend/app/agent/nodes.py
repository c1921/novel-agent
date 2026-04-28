from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app import crud, models
from app.agent.llm import chat_completion, json_completion
from app.agent.prompts import (
    CONSISTENCY_PROMPT,
    DRAFT_PROMPT,
    OUTLINE_PROMPT,
    PLOT_QUESTIONS_PROMPT,
    POLISH_PROMPT,
)
from app.agent.state import NovelAgentState
from app.rag.retriever import retrieve_project_context


def _state(state: NovelAgentState) -> NovelAgentState:
    return dict(state)


def _append_message(state: NovelAgentState, role: str, content: str) -> None:
    state.setdefault("messages", []).append({"role": role, "content": content})


def _project_context(db: Session, project_id: int) -> str:
    project = crud.get_project_detail(db, project_id)
    if not project:
        return ""
    parts = [
        f"项目：{project.title}",
        f"类型：{project.genre}",
        f"目标读者：{project.target_audience}",
        f"风格指南：{project.style_guide}",
        "\n人物卡：",
    ]
    for character in project.characters:
        parts.append(
            f"- {character.name}（{character.role}）：性格={character.personality}；目标={character.goal}；"
            f"说话风格={character.speech_style}；约束={character.constraints}；背景={character.background}"
        )
    parts.append("\n世界观：")
    for setting in project.world_settings:
        parts.append(f"- [{setting.category}] {setting.title}: {setting.content}")
    parts.append("\n全局大纲：")
    for outline in project.outlines:
        parts.append(f"- {outline.title}: {outline.content}")
    parts.append("\n已写章节：")
    for chapter in project.chapters:
        summary = chapter.outline or chapter.polished_draft or chapter.draft
        parts.append(f"- 第{chapter.chapter_number}章 {chapter.title}: {summary[:600]}")
    parts.append("\n伏笔：")
    for item in project.foreshadowings:
        parts.append(f"- {item.name}: 埋设={item.setup}；回收计划={item.payoff_plan}；状态={item.status}")
    return "\n".join(parts)


def load_project_context(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    next_state["project_context"] = _project_context(db, int(next_state["project_id"]))
    _append_message(next_state, "system", "Loaded project context.")
    return next_state


def retrieve_relevant_knowledge(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    query = f"{next_state.get('user_goal', '')}\n{next_state.get('project_context', '')[:1000]}"
    next_state["retrieved_context"] = retrieve_project_context(
        int(next_state["project_id"]), query, db, top_k=6
    )
    _append_message(next_state, "system", "Retrieved project knowledge.")
    return next_state


def _normalize_questions(raw: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    questions = raw.get("questions") or []
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(questions[:5], start=1):
        question_type = item.get("type", "optional")
        if question_type not in {"must_ask", "optional", "auto_decidable"}:
            question_type = "optional"
        normalized.append(
            {
                "id": str(item.get("id") or f"q{index}"),
                "type": question_type,
                "question": str(item.get("question") or "这个剧情点希望如何处理？"),
                "reason": str(item.get("reason") or ""),
                "options": [str(option) for option in item.get("options", [])],
            }
        )

    defaults = [
        {
            "id": "q1",
            "type": "must_ask",
            "question": "本章结尾是否要揭示重大真相，还是只留下线索？",
            "reason": "结尾揭示程度会影响主线推进速度。",
            "options": ["揭示重大真相", "只留下线索", "设置误导"],
        },
        {
            "id": "q2",
            "type": "must_ask",
            "question": "本章是否允许改变核心人物关系？",
            "reason": "人物关系变化属于重大剧情决策。",
            "options": ["不改变", "轻微推进", "明显改变"],
        },
        {
            "id": "q3",
            "type": "optional",
            "question": "本章整体氛围应更偏紧张、温情还是悬疑？",
            "reason": "氛围会影响正文节奏和描写选择。",
            "options": ["紧张", "温情", "悬疑"],
        },
    ]
    while len(normalized) < 3:
        normalized.append(defaults[len(normalized)])
    if not any(item["type"] == "must_ask" for item in normalized):
        normalized[0]["type"] = "must_ask"
    auto_decidable = [str(item) for item in raw.get("auto_decidable", [])] or [
        "天气",
        "普通动作衔接",
        "非关键环境描写",
    ]
    return normalized[:5], auto_decidable


def generate_plot_questions(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    payload = json.dumps(
        {
            "project_context": next_state.get("project_context", ""),
            "retrieved_context": next_state.get("retrieved_context", []),
            "user_goal": next_state.get("user_goal", ""),
        },
        ensure_ascii=False,
    )
    raw = json_completion(
        [
            {"role": "system", "content": PLOT_QUESTIONS_PROMPT},
            {"role": "user", "content": payload},
        ],
        temperature=0.3,
    )
    questions, auto_decidable = _normalize_questions(raw)
    next_state["plot_questions"] = questions
    next_state["auto_decidable"] = auto_decidable
    next_state["next_action"] = "answer_plot_questions"
    _append_message(next_state, "assistant", "Generated plot questions.")
    return next_state


def generate_chapter_outline(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    payload = json.dumps(
        {
            "project_context": next_state.get("project_context") or _project_context(
                db, int(next_state["project_id"])
            ),
            "retrieved_context": next_state.get("retrieved_context", []),
            "user_goal": next_state.get("user_goal", ""),
            "plot_questions": next_state.get("plot_questions", []),
            "user_answers": next_state.get("user_answers", []),
            "revision_instruction": next_state.get("outline_revision_instruction", ""),
        },
        ensure_ascii=False,
    )
    outline = chat_completion(
        [
            {"role": "system", "content": OUTLINE_PROMPT},
            {"role": "user", "content": payload},
        ],
        temperature=0.5,
    )
    next_state["chapter_outline"] = outline
    next_state["next_action"] = "approve_outline"
    _append_message(next_state, "assistant", "Generated chapter outline.")
    return next_state


def generate_draft(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    payload = json.dumps(
        {
            "project_context": next_state.get("project_context") or _project_context(
                db, int(next_state["project_id"])
            ),
            "retrieved_context": next_state.get("retrieved_context", []),
            "user_goal": next_state.get("user_goal", ""),
            "approved_outline": next_state.get("chapter_outline", ""),
            "user_answers": next_state.get("user_answers", []),
        },
        ensure_ascii=False,
    )
    next_state["draft"] = chat_completion(
        [
            {"role": "system", "content": DRAFT_PROMPT},
            {"role": "user", "content": payload},
        ],
        temperature=0.7,
    )
    _append_message(next_state, "assistant", "Generated draft.")
    return next_state


def polish_draft(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    payload = json.dumps(
        {
            "approved_outline": next_state.get("chapter_outline", ""),
            "draft": next_state.get("draft", ""),
        },
        ensure_ascii=False,
    )
    next_state["polished_draft"] = chat_completion(
        [
            {"role": "system", "content": POLISH_PROMPT},
            {"role": "user", "content": payload},
        ],
        temperature=0.5,
    )
    _append_message(next_state, "assistant", "Polished draft.")
    return next_state


def consistency_check(state: NovelAgentState, db: Session) -> NovelAgentState:
    next_state = _state(state)
    payload = json.dumps(
        {
            "project_context": next_state.get("project_context") or _project_context(
                db, int(next_state["project_id"])
            ),
            "retrieved_context": next_state.get("retrieved_context", []),
            "approved_outline": next_state.get("chapter_outline", ""),
            "draft": next_state.get("polished_draft") or next_state.get("draft", ""),
        },
        ensure_ascii=False,
    )
    report = json_completion(
        [
            {"role": "system", "content": CONSISTENCY_PROMPT},
            {"role": "user", "content": payload},
        ],
        temperature=0.2,
    )
    report.setdefault("summary", "一致性检查完成。")
    report.setdefault("issues", [])
    next_state["consistency_report"] = report
    next_state["next_action"] = "review_draft"
    _append_message(next_state, "assistant", "Completed consistency check.")
    return next_state


def save_chapter_from_state(state: NovelAgentState, db: Session, use_polished: bool) -> models.Chapter:
    chapter = db.get(models.Chapter, int(state["chapter_id"]))
    if not chapter:
        raise ValueError("Chapter not found")
    chapter.goal = state.get("user_goal", chapter.goal)
    chapter.outline = state.get("chapter_outline", chapter.outline)
    chapter.draft = state.get("draft", chapter.draft)
    chapter.polished_draft = state.get("polished_draft", chapter.polished_draft)
    if use_polished:
        chapter.draft = chapter.polished_draft or chapter.draft
    chapter.status = "saved"
    db.commit()
    db.refresh(chapter)
    return chapter

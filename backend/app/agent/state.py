from __future__ import annotations

from typing import Any, TypedDict


class NovelAgentState(TypedDict, total=False):
    project_id: int
    chapter_id: int
    user_goal: str
    project_context: str
    retrieved_context: list[str]
    plot_questions: list[dict[str, Any]]
    auto_decidable: list[str]
    user_answers: list[dict[str, str]]
    chapter_outline: str
    outline_revision_instruction: str
    outline_approved: bool
    draft: str
    polished_draft: str
    consistency_report: dict[str, Any]
    next_action: str
    messages: list[dict[str, str]]

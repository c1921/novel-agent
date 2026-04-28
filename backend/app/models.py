from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.utcnow()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(120), default="")
    target_audience: Mapped[str] = mapped_column(String(200), default="")
    style_guide: Mapped[str] = mapped_column(Text, default="")

    characters: Mapped[list[Character]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    world_settings: Mapped[list[WorldSetting]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    outlines: Mapped[list[Outline]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    chapters: Mapped[list[Chapter]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    foreshadowings: Mapped[list[Foreshadowing]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    agent_sessions: Mapped[list[AgentSession]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[str] = mapped_column(String(120), default="")
    personality: Mapped[str] = mapped_column(Text, default="")
    goal: Mapped[str] = mapped_column(Text, default="")
    speech_style: Mapped[str] = mapped_column(Text, default="")
    constraints: Mapped[str] = mapped_column(Text, default="")
    background: Mapped[str] = mapped_column(Text, default="")

    project: Mapped[Project] = relationship(back_populates="characters")


class WorldSetting(Base):
    __tablename__ = "world_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), default="")

    project: Mapped[Project] = relationship(back_populates="world_settings")


class Outline(Base):
    __tablename__ = "outlines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")

    project: Mapped[Project] = relationship(back_populates="outlines")


class Chapter(TimestampMixin, Base):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), default="")
    goal: Mapped[str] = mapped_column(Text, default="")
    outline: Mapped[str] = mapped_column(Text, default="")
    draft: Mapped[str] = mapped_column(Text, default="")
    polished_draft: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="planned")

    project: Mapped[Project] = relationship(back_populates="chapters")


class Foreshadowing(Base):
    __tablename__ = "foreshadowings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    setup: Mapped[str] = mapped_column(Text, default="")
    payoff_plan: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(80), default="planned")

    project: Mapped[Project] = relationship(back_populates="foreshadowings")


class AgentSession(TimestampMixin, Base):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), index=True)
    next_action: Mapped[str] = mapped_column(String(80), default="answer_plot_questions")
    state_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    project: Mapped[Project] = relationship(back_populates="agent_sessions")
    chapter: Mapped[Chapter] = relationship()

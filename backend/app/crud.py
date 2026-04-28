from __future__ import annotations

from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models, schemas

ModelT = TypeVar("ModelT")


def apply_update(instance: ModelT, payload: BaseModel) -> ModelT:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(instance, key, value)
    return instance


def get_project(db: Session, project_id: int) -> models.Project | None:
    return db.get(models.Project, project_id)


def get_project_detail(db: Session, project_id: int) -> models.Project | None:
    stmt = (
        select(models.Project)
        .where(models.Project.id == project_id)
        .options(
            selectinload(models.Project.characters),
            selectinload(models.Project.world_settings),
            selectinload(models.Project.outlines),
            selectinload(models.Project.chapters),
            selectinload(models.Project.foreshadowings),
        )
    )
    return db.scalar(stmt)


def list_projects(db: Session) -> Sequence[models.Project]:
    return db.scalars(select(models.Project).order_by(models.Project.updated_at.desc())).all()


def create_project(db: Session, payload: schemas.ProjectCreate) -> models.Project:
    project = models.Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project: models.Project, payload: schemas.ProjectUpdate) -> models.Project:
    apply_update(project, payload)
    db.commit()
    db.refresh(project)
    return project


def delete_instance(db: Session, instance: Any) -> None:
    db.delete(instance)
    db.commit()


def create_character(
    db: Session, project_id: int, payload: schemas.CharacterCreate
) -> models.Character:
    item = models.Character(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_characters(db: Session, project_id: int) -> Sequence[models.Character]:
    return db.scalars(
        select(models.Character).where(models.Character.project_id == project_id).order_by(models.Character.id)
    ).all()


def create_world_setting(
    db: Session, project_id: int, payload: schemas.WorldSettingCreate
) -> models.WorldSetting:
    item = models.WorldSetting(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_world_settings(db: Session, project_id: int) -> Sequence[models.WorldSetting]:
    return db.scalars(
        select(models.WorldSetting)
        .where(models.WorldSetting.project_id == project_id)
        .order_by(models.WorldSetting.id)
    ).all()


def create_outline(db: Session, project_id: int, payload: schemas.OutlineCreate) -> models.Outline:
    item = models.Outline(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_outlines(db: Session, project_id: int) -> Sequence[models.Outline]:
    return db.scalars(
        select(models.Outline).where(models.Outline.project_id == project_id).order_by(models.Outline.id)
    ).all()


def next_chapter_number(db: Session, project_id: int) -> int:
    max_number = db.scalar(
        select(func.max(models.Chapter.chapter_number)).where(models.Chapter.project_id == project_id)
    )
    return int(max_number or 0) + 1


def create_chapter(db: Session, project_id: int, payload: schemas.ChapterCreate) -> models.Chapter:
    item = models.Chapter(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_chapters(db: Session, project_id: int) -> Sequence[models.Chapter]:
    return db.scalars(
        select(models.Chapter)
        .where(models.Chapter.project_id == project_id)
        .order_by(models.Chapter.chapter_number, models.Chapter.id)
    ).all()


def create_foreshadowing(
    db: Session, project_id: int, payload: schemas.ForeshadowingCreate
) -> models.Foreshadowing:
    item = models.Foreshadowing(project_id=project_id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_foreshadowings(db: Session, project_id: int) -> Sequence[models.Foreshadowing]:
    return db.scalars(
        select(models.Foreshadowing)
        .where(models.Foreshadowing.project_id == project_id)
        .order_by(models.Foreshadowing.id)
    ).all()

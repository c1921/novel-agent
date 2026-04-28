from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.projects import get_project_or_404
from app.database import get_db

router = APIRouter(prefix="/api/projects/{project_id}/characters", tags=["characters"])
logger = logging.getLogger(__name__)


def get_character_or_404(project_id: int, character_id: int, db: Session) -> models.Character:
    item = db.get(models.Character, character_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    return item


@router.get("", response_model=list[schemas.CharacterRead])
def list_characters(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return crud.list_characters(db, project_id)


@router.post("", response_model=schemas.CharacterRead, status_code=status.HTTP_201_CREATED)
def create_character(
    project_id: int,
    payload: schemas.CharacterCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)
    item = crud.create_character(db, project_id, payload)
    logger.info("crud.create resource=character project_id=%s entity_id=%s", project_id, item.id)
    return item


@router.patch("/{character_id}", response_model=schemas.CharacterRead)
def update_character(
    project_id: int,
    character_id: int,
    payload: schemas.CharacterUpdate,
    db: Session = Depends(get_db),
):
    item = get_character_or_404(project_id, character_id, db)
    crud.apply_update(item, payload)
    db.commit()
    db.refresh(item)
    logger.info(
        "crud.update resource=character project_id=%s entity_id=%s fields=%s",
        project_id,
        character_id,
        ",".join(payload.model_dump(exclude_unset=True).keys()),
    )
    return item


@router.delete("/{character_id}")
def delete_character(project_id: int, character_id: int, db: Session = Depends(get_db)):
    item = get_character_or_404(project_id, character_id, db)
    crud.delete_instance(db, item)
    logger.info("crud.delete resource=character project_id=%s entity_id=%s", project_id, character_id)
    return {"ok": True}

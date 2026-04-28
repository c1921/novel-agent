from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.projects import get_project_or_404
from app.database import get_db

router = APIRouter(prefix="/api/projects/{project_id}/outlines", tags=["outlines"])
logger = logging.getLogger(__name__)


def get_outline_or_404(project_id: int, outline_id: int, db: Session) -> models.Outline:
    item = db.get(models.Outline, outline_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Outline not found")
    return item


@router.get("", response_model=list[schemas.OutlineRead])
def list_outlines(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return crud.list_outlines(db, project_id)


@router.post("", response_model=schemas.OutlineRead, status_code=status.HTTP_201_CREATED)
def create_outline(
    project_id: int,
    payload: schemas.OutlineCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)
    item = crud.create_outline(db, project_id, payload)
    logger.info("crud.create resource=outline project_id=%s entity_id=%s", project_id, item.id)
    return item


@router.patch("/{outline_id}", response_model=schemas.OutlineRead)
def update_outline(
    project_id: int,
    outline_id: int,
    payload: schemas.OutlineUpdate,
    db: Session = Depends(get_db),
):
    item = get_outline_or_404(project_id, outline_id, db)
    crud.apply_update(item, payload)
    db.commit()
    db.refresh(item)
    logger.info(
        "crud.update resource=outline project_id=%s entity_id=%s fields=%s",
        project_id,
        outline_id,
        ",".join(payload.model_dump(exclude_unset=True).keys()),
    )
    return item


@router.delete("/{outline_id}")
def delete_outline(project_id: int, outline_id: int, db: Session = Depends(get_db)):
    item = get_outline_or_404(project_id, outline_id, db)
    crud.delete_instance(db, item)
    logger.info("crud.delete resource=outline project_id=%s entity_id=%s", project_id, outline_id)
    return {"ok": True}

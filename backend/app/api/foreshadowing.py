from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.projects import get_project_or_404
from app.database import get_db

router = APIRouter(prefix="/api/projects/{project_id}/foreshadowing", tags=["foreshadowing"])
logger = logging.getLogger(__name__)


def get_foreshadowing_or_404(
    project_id: int, foreshadowing_id: int, db: Session
) -> models.Foreshadowing:
    item = db.get(models.Foreshadowing, foreshadowing_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Foreshadowing not found")
    return item


@router.get("", response_model=list[schemas.ForeshadowingRead])
def list_foreshadowings(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return crud.list_foreshadowings(db, project_id)


@router.post("", response_model=schemas.ForeshadowingRead, status_code=status.HTTP_201_CREATED)
def create_foreshadowing(
    project_id: int,
    payload: schemas.ForeshadowingCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)
    item = crud.create_foreshadowing(db, project_id, payload)
    logger.info("crud.create resource=foreshadowing project_id=%s entity_id=%s", project_id, item.id)
    return item


@router.patch("/{foreshadowing_id}", response_model=schemas.ForeshadowingRead)
def update_foreshadowing(
    project_id: int,
    foreshadowing_id: int,
    payload: schemas.ForeshadowingUpdate,
    db: Session = Depends(get_db),
):
    item = get_foreshadowing_or_404(project_id, foreshadowing_id, db)
    crud.apply_update(item, payload)
    db.commit()
    db.refresh(item)
    logger.info(
        "crud.update resource=foreshadowing project_id=%s entity_id=%s fields=%s",
        project_id,
        foreshadowing_id,
        ",".join(payload.model_dump(exclude_unset=True).keys()),
    )
    return item


@router.delete("/{foreshadowing_id}")
def delete_foreshadowing(
    project_id: int, foreshadowing_id: int, db: Session = Depends(get_db)
):
    item = get_foreshadowing_or_404(project_id, foreshadowing_id, db)
    crud.delete_instance(db, item)
    logger.info("crud.delete resource=foreshadowing project_id=%s entity_id=%s", project_id, foreshadowing_id)
    return {"ok": True}

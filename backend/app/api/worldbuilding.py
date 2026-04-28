from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.projects import get_project_or_404
from app.database import get_db

router = APIRouter(prefix="/api/projects/{project_id}/worldbuilding", tags=["worldbuilding"])
logger = logging.getLogger(__name__)


def get_world_setting_or_404(
    project_id: int, setting_id: int, db: Session
) -> models.WorldSetting:
    item = db.get(models.WorldSetting, setting_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World setting not found")
    return item


@router.get("", response_model=list[schemas.WorldSettingRead])
def list_world_settings(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return crud.list_world_settings(db, project_id)


@router.post("", response_model=schemas.WorldSettingRead, status_code=status.HTTP_201_CREATED)
def create_world_setting(
    project_id: int,
    payload: schemas.WorldSettingCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)
    item = crud.create_world_setting(db, project_id, payload)
    logger.info("crud.create resource=world_setting project_id=%s entity_id=%s", project_id, item.id)
    return item


@router.patch("/{setting_id}", response_model=schemas.WorldSettingRead)
def update_world_setting(
    project_id: int,
    setting_id: int,
    payload: schemas.WorldSettingUpdate,
    db: Session = Depends(get_db),
):
    item = get_world_setting_or_404(project_id, setting_id, db)
    crud.apply_update(item, payload)
    db.commit()
    db.refresh(item)
    logger.info(
        "crud.update resource=world_setting project_id=%s entity_id=%s fields=%s",
        project_id,
        setting_id,
        ",".join(payload.model_dump(exclude_unset=True).keys()),
    )
    return item


@router.delete("/{setting_id}")
def delete_world_setting(project_id: int, setting_id: int, db: Session = Depends(get_db)):
    item = get_world_setting_or_404(project_id, setting_id, db)
    crud.delete_instance(db, item)
    logger.info("crud.delete resource=world_setting project_id=%s entity_id=%s", project_id, setting_id)
    return {"ok": True}

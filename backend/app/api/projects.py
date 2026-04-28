from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.rag.indexer import rebuild_project_index

router = APIRouter(prefix="/api/projects", tags=["projects"])
logger = logging.getLogger(__name__)


def get_project_or_404(project_id: int, db: Session):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.get("", response_model=list[schemas.ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return crud.list_projects(db)


@router.post("", response_model=schemas.ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = crud.create_project(db, payload)
    logger.info("crud.create resource=project project_id=%s title_chars=%s", project.id, len(project.title))
    return project


@router.get("/{project_id}", response_model=schemas.ProjectDetail)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project_detail(db, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=schemas.ProjectRead)
def update_project(
    project_id: int,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)
    project = crud.update_project(db, project, payload)
    logger.info("crud.update resource=project project_id=%s fields=%s", project_id, ",".join(payload.model_dump(exclude_unset=True).keys()))
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)
    crud.delete_instance(db, project)
    logger.info("crud.delete resource=project project_id=%s", project_id)
    return {"ok": True}


@router.post("/{project_id}/rebuild-index", response_model=schemas.IndexResponse)
def rebuild_index(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    result = rebuild_project_index(project_id, db)
    logger.info(
        "rag.rebuild_api project_id=%s documents=%s backend=%s",
        project_id,
        result.document_count if hasattr(result, "document_count") else result["document_count"],
        result.backend if hasattr(result, "backend") else result["backend"],
    )
    return result

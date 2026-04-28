from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.rag.indexer import rebuild_project_index

router = APIRouter(prefix="/api/projects", tags=["projects"])


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
    return crud.create_project(db, payload)


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
    return crud.update_project(db, project, payload)


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)
    crud.delete_instance(db, project)
    return {"ok": True}


@router.post("/{project_id}/rebuild-index", response_model=schemas.IndexResponse)
def rebuild_index(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return rebuild_project_index(project_id, db)

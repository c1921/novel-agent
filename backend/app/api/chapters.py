from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api.projects import get_project_or_404
from app.database import get_db

router = APIRouter(prefix="/api/projects/{project_id}/chapters", tags=["chapters"])


def get_chapter_or_404(project_id: int, chapter_id: int, db: Session) -> models.Chapter:
    item = db.get(models.Chapter, chapter_id)
    if not item or item.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return item


@router.get("", response_model=list[schemas.ChapterRead])
def list_chapters(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return crud.list_chapters(db, project_id)


@router.post("", response_model=schemas.ChapterRead, status_code=status.HTTP_201_CREATED)
def create_chapter(
    project_id: int,
    payload: schemas.ChapterCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)
    return crud.create_chapter(db, project_id, payload)


@router.get("/{chapter_id}", response_model=schemas.ChapterRead)
def get_chapter(project_id: int, chapter_id: int, db: Session = Depends(get_db)):
    return get_chapter_or_404(project_id, chapter_id, db)


@router.patch("/{chapter_id}", response_model=schemas.ChapterRead)
def update_chapter(
    project_id: int,
    chapter_id: int,
    payload: schemas.ChapterUpdate,
    db: Session = Depends(get_db),
):
    item = get_chapter_or_404(project_id, chapter_id, db)
    crud.apply_update(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{chapter_id}")
def delete_chapter(project_id: int, chapter_id: int, db: Session = Depends(get_db)):
    item = get_chapter_or_404(project_id, chapter_id, db)
    crud.delete_instance(db, item)
    return {"ok": True}

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.config import settings


def project_index_dir(project_id: int) -> Path:
    return settings.index_storage_path / str(project_id)


def collect_project_documents(db: Session, project_id: int) -> list[dict[str, Any]]:
    project = db.get(models.Project, project_id)
    if not project:
        return []

    docs: list[dict[str, Any]] = [
        {
            "id": f"project-{project.id}",
            "title": f"项目：{project.title}",
            "kind": "project",
            "text": "\n".join(
                [
                    f"项目标题：{project.title}",
                    f"类型：{project.genre}",
                    f"目标读者：{project.target_audience}",
                    f"风格指南：{project.style_guide}",
                ]
            ),
        }
    ]

    for character in project.characters:
        docs.append(
            {
                "id": f"character-{character.id}",
                "title": f"人物：{character.name}",
                "kind": "character",
                "text": "\n".join(
                    [
                        f"人物：{character.name}",
                        f"角色：{character.role}",
                        f"性格：{character.personality}",
                        f"目标：{character.goal}",
                        f"说话风格：{character.speech_style}",
                        f"约束：{character.constraints}",
                        f"背景：{character.background}",
                    ]
                ),
            }
        )

    for setting in project.world_settings:
        docs.append(
            {
                "id": f"world-{setting.id}",
                "title": f"世界观：{setting.title}",
                "kind": "worldbuilding",
                "text": f"世界观分类：{setting.category}\n标题：{setting.title}\n内容：{setting.content}",
            }
        )

    for outline in project.outlines:
        docs.append(
            {
                "id": f"outline-{outline.id}",
                "title": f"大纲：{outline.title}",
                "kind": "outline",
                "text": f"大纲标题：{outline.title}\n内容：{outline.content}",
            }
        )

    for chapter in project.chapters:
        docs.append(
            {
                "id": f"chapter-{chapter.id}",
                "title": f"章节：{chapter.chapter_number} {chapter.title}",
                "kind": "chapter",
                "text": "\n".join(
                    [
                        f"章节：第{chapter.chapter_number}章 {chapter.title}",
                        f"目标：{chapter.goal}",
                        f"大纲：{chapter.outline}",
                        f"正文：{chapter.polished_draft or chapter.draft}",
                    ]
                ),
            }
        )

    for item in project.foreshadowings:
        docs.append(
            {
                "id": f"foreshadowing-{item.id}",
                "title": f"伏笔：{item.name}",
                "kind": "foreshadowing",
                "text": "\n".join(
                    [
                        f"伏笔：{item.name}",
                        f"埋设：{item.setup}",
                        f"回收计划：{item.payoff_plan}",
                        f"状态：{item.status}",
                    ]
                ),
            }
        )

    return docs


def _persist_documents(index_dir: Path, documents: list[dict[str, Any]]) -> None:
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "documents.json").write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def rebuild_project_index(project_id: int, db: Session) -> dict[str, Any]:
    documents = collect_project_documents(db, project_id)
    index_dir = project_index_dir(project_id)
    _persist_documents(index_dir, documents)

    backend = "keyword"
    if documents:
        try:
            from llama_index.core import Document, Settings, VectorStoreIndex
            from llama_index.core.embeddings import MockEmbedding

            Settings.embed_model = MockEmbedding(embed_dim=384)
            llama_documents = [
                Document(
                    text=doc["text"],
                    metadata={"id": doc["id"], "title": doc["title"], "kind": doc["kind"]},
                )
                for doc in documents
            ]
            index = VectorStoreIndex.from_documents(llama_documents)
            index.storage_context.persist(persist_dir=str(index_dir / "llama"))
            backend = "llama-index"
        except Exception:
            backend = "keyword"

    return {
        "project_id": project_id,
        "document_count": len(documents),
        "backend": backend,
        "message": "Index rebuilt" if documents else "Project has no documents to index",
    }

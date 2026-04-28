from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.rag.indexer import collect_project_documents, project_index_dir, rebuild_project_index


def _load_documents(index_dir: Path) -> list[dict[str, Any]]:
    documents_path = index_dir / "documents.json"
    if not documents_path.exists():
        return []
    return json.loads(documents_path.read_text(encoding="utf-8"))


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[\w\u4e00-\u9fff]+", text.lower())
    chars = [char for char in text.lower() if "\u4e00" <= char <= "\u9fff"]
    return set(words + chars)


def _keyword_retrieve(documents: list[dict[str, Any]], query: str, top_k: int) -> list[str]:
    query_tokens = _tokens(query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for doc in documents:
        doc_tokens = _tokens(f"{doc.get('title', '')}\n{doc.get('text', '')}")
        score = len(query_tokens & doc_tokens)
        if score:
            scored.append((score, doc))
    if not scored:
        scored = [(0, doc) for doc in documents]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [f"[{doc['kind']}] {doc['title']}\n{doc['text']}" for _, doc in scored[:top_k]]


def retrieve_project_context(project_id: int, query: str, db: Session, top_k: int = 6) -> list[str]:
    index_dir = project_index_dir(project_id)
    documents = _load_documents(index_dir)
    if not documents:
        documents = collect_project_documents(db, project_id)
        if documents:
            rebuild_project_index(project_id, db)

    if not documents:
        return []

    llama_dir = index_dir / "llama"
    if llama_dir.exists():
        try:
            from llama_index.core import Settings, StorageContext, load_index_from_storage
            from llama_index.core.embeddings import MockEmbedding

            Settings.embed_model = MockEmbedding(embed_dim=384)
            storage_context = StorageContext.from_defaults(persist_dir=str(llama_dir))
            index = load_index_from_storage(storage_context)
            retriever = index.as_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query)
            return [node.get_content() for node in nodes]
        except Exception:
            pass

    return _keyword_retrieve(documents, query, top_k)

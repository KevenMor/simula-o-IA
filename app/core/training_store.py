"""Simple file-based training data store (no database required).

This is meant for early-stage experimentation: it stores training documents
per tenant in a JSON file under `data/training_data.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from app.utils.logger import logger


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_FILE = DATA_DIR / "training_data.json"


@dataclass
class TrainingDocument:
    """Represents a simple training document for a tenant."""

    id: str
    tenant_id: str
    title: str
    category: str
    content: str
    created_at: str
    updated_at: str


def _ensure_data_dir() -> None:
    """Ensure that the data directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw() -> Dict[str, Any]:
    """Load raw JSON structure from disk."""
    _ensure_data_dir()
    if not DATA_FILE.exists():
        return {"documents": []}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load training data: {exc}")
        return {"documents": []}


def _save_raw(data: Dict[str, Any]) -> None:
    """Persist raw JSON structure to disk."""
    _ensure_data_dir()
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error(f"Failed to save training data: {exc}")


def list_documents(tenant_id: str) -> List[TrainingDocument]:
    """Return all documents for a given tenant."""
    raw = _load_raw()
    docs: List[TrainingDocument] = []
    for item in raw.get("documents", []):
        if item.get("tenant_id") == tenant_id:
            docs.append(TrainingDocument(**item))
    return docs


def upsert_document(
    tenant_id: str,
    title: str,
    category: str,
    content: str,
    doc_id: str | None = None,
) -> TrainingDocument:
    """Create or update a training document.

    If `doc_id` is None, a new document is created.
    """
    from uuid import uuid4

    raw = _load_raw()
    documents: List[Dict[str, Any]] = raw.setdefault("documents", [])
    now = datetime.utcnow().isoformat()

    if doc_id is None:
        doc_id = uuid4().hex
        doc = TrainingDocument(
            id=doc_id,
            tenant_id=tenant_id,
            title=title,
            category=category,
            content=content,
            created_at=now,
            updated_at=now,
        )
        documents.append(asdict(doc))
        logger.info(f"Created training document {doc_id} for tenant {tenant_id}")
    else:
        updated = False
        for item in documents:
            if item.get("id") == doc_id and item.get("tenant_id") == tenant_id:
                item.update(
                    {
                        "title": title,
                        "category": category,
                        "content": content,
                        "updated_at": now,
                    }
                )
                updated = True
                logger.info(f"Updated training document {doc_id} for tenant {tenant_id}")
                break
        if not updated:
            doc = TrainingDocument(
                id=doc_id,
                tenant_id=tenant_id,
                title=title,
                category=category,
                content=content,
                created_at=now,
                updated_at=now,
            )
            documents.append(asdict(doc))
            logger.info(
                f"Created training document {doc_id} for tenant {tenant_id} (upsert)"
            )

    _save_raw(raw)

    # Return latest version
    for item in documents:
        if item.get("id") == doc_id and item.get("tenant_id") == tenant_id:
            return TrainingDocument(**item)

    # Fallback (should not happen)
    return TrainingDocument(
        id=doc_id,
        tenant_id=tenant_id,
        title=title,
        category=category,
        content=content,
        created_at=now,
        updated_at=now,
    )


def delete_document(tenant_id: str, doc_id: str) -> bool:
    """Delete a document by id and tenant. Returns True if removed."""
    raw = _load_raw()
    documents: List[Dict[str, Any]] = raw.setdefault("documents", [])
    before = len(documents)
    documents = [
        item
        for item in documents
        if not (item.get("id") == doc_id and item.get("tenant_id") == tenant_id)
    ]
    raw["documents"] = documents
    _save_raw(raw)
    removed = len(documents) < before
    if removed:
        logger.info(f"Deleted training document {doc_id} for tenant {tenant_id}")
    return removed


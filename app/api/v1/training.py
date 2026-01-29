"""Training endpoints for managing simple knowledge documents per tenant.

This version stores data in a local JSON file (no database), just to support
early experimentation and UI flows.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.training_store import (
    TrainingDocument,
    list_documents,
    upsert_document,
    delete_document,
)
from app.utils.auth import verify_api_key
from app.utils.validators import (
    sanitize_text,
    sanitize_text_preserve_newlines,
    validate_knowledge_base_id,
)
from app.utils.logger import logger


class TrainingDocumentIn(BaseModel):
    """Payload for creating/updating a training document."""

    tenant_id: str = Field(..., description="Client/tenant identifier")
    title: str = Field(..., description="Document title")
    category: str = Field("geral", description="Category or topic")
    content: str = Field(..., description="Raw text content")
    id: Optional[str] = Field(None, description="Existing document id for update")


class TrainingDocumentOut(BaseModel):
    """Training document as returned to clients."""

    id: str
    tenant_id: str
    title: str
    category: str
    content: str
    created_at: str
    updated_at: str


router = APIRouter(prefix="/training", tags=["Training"])


@router.get(
    "/documents",
    response_model=List[TrainingDocumentOut],
    dependencies=[Depends(verify_api_key)],
)
async def get_documents(tenant_id: str = Query(..., description="Tenant id")):
    """List all training documents for a given tenant."""
    if not validate_knowledge_base_id(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant id invalido")

    docs = list_documents(tenant_id)
    return [TrainingDocumentOut(**doc.__dict__) for doc in docs]


@router.post(
    "/documents",
    response_model=TrainingDocumentOut,
    dependencies=[Depends(verify_api_key)],
)
async def create_or_update_document(payload: TrainingDocumentIn):
    """Create or update a training document for a tenant."""
    tenant_id = payload.tenant_id
    if not validate_knowledge_base_id(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant id invalido")

    title = sanitize_text(payload.title, max_length=200)
    # Conteudo pode ser Markdown longo; preservar quebras de linha
    content = sanitize_text_preserve_newlines(payload.content, max_length=100000)
    category = sanitize_text(payload.category, max_length=100) or "geral"

    if not title or not content:
        raise HTTPException(
            status_code=400, detail="Titulo e conteudo nao podem estar vazios"
        )

    doc: TrainingDocument = upsert_document(
        tenant_id=tenant_id,
        title=title,
        category=category,
        content=content,
        doc_id=payload.id,
    )

    logger.info(
        "Training document saved",
    )

    return TrainingDocumentOut(**doc.__dict__)


@router.delete(
    "/documents/{doc_id}",
    dependencies=[Depends(verify_api_key)],
)
async def remove_document(tenant_id: str, doc_id: str):
    """Delete a training document."""
    if not validate_knowledge_base_id(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant id invalido")

    removed = delete_document(tenant_id, doc_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Documento nao encontrado")

    return {"status": "ok", "deleted": True}


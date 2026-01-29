"""Settings/configuration endpoints for tenants."""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
import json
import os
from pathlib import Path

from app.utils.auth import verify_api_key
from app.utils.validators import validate_knowledge_base_id
from app.utils.logger import logger


class TenantSettings(BaseModel):
    """Settings model for a tenant."""
    
    tenant_id: str
    # Anti-hallucination settings
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0, description="Minimum confidence score")
    enable_hallucination_check: bool = Field(True, description="Enable hallucination validation")
    # LLM settings
    temperature: float = Field(0.3, ge=0.0, le=2.0, description="LLM temperature (lower = less creative)")
    max_tokens: int = Field(1000, ge=50, le=4000, description="Max tokens per response")
    # Response settings
    response_style: str = Field("friendly", description="Response style: friendly, formal, casual")
    auto_ask_name: bool = Field(True, description="Automatically ask for customer name")
    # Cache settings
    cache_enabled: bool = Field(True, description="Enable response caching")
    cache_ttl_seconds: int = Field(300, ge=60, le=3600, description="Cache TTL in seconds")


class TenantSettingsUpdate(BaseModel):
    """Update model for tenant settings."""
    
    confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    enable_hallucination_check: Optional[bool] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=50, le=4000)
    response_style: Optional[str] = None
    auto_ask_name: Optional[bool] = None
    cache_enabled: Optional[bool] = None
    cache_ttl_seconds: Optional[int] = Field(None, ge=60, le=3600)


router = APIRouter(prefix="/settings", tags=["Settings"])


def get_settings_file_path() -> Path:
    """Get path to settings JSON file."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    return data_dir / "tenant_settings.json"


def load_all_settings() -> dict:
    """Load all tenant settings from file."""
    settings_file = get_settings_file_path()
    if not settings_file.exists():
        return {}
    
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading settings: {e}")
        return {}


def save_all_settings(settings: dict):
    """Save all tenant settings to file."""
    settings_file = get_settings_file_path()
    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        raise


@router.get("/{tenant_id}", response_model=TenantSettings, dependencies=[Depends(verify_api_key)])
async def get_settings(tenant_id: str):
    """Get settings for a tenant."""
    if not validate_knowledge_base_id(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant id invalido")
    
    all_settings = load_all_settings()
    tenant_data = all_settings.get(tenant_id)
    
    if not tenant_data:
        # Return defaults
        return TenantSettings(tenant_id=tenant_id)
    
    return TenantSettings(**tenant_data)


@router.put("/{tenant_id}", response_model=TenantSettings, dependencies=[Depends(verify_api_key)])
async def update_settings(tenant_id: str, updates: TenantSettingsUpdate):
    """Update settings for a tenant."""
    if not validate_knowledge_base_id(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant id invalido")
    
    all_settings = load_all_settings()
    
    # Get current settings or defaults
    current = all_settings.get(tenant_id, {})
    current_settings = TenantSettings(tenant_id=tenant_id, **current)
    
    # Apply updates
    update_dict = updates.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(current_settings, key, value)
    
    # Save
    all_settings[tenant_id] = current_settings.model_dump()
    save_all_settings(all_settings)
    
    logger.info(f"Settings updated for tenant: {tenant_id}")
    
    return current_settings

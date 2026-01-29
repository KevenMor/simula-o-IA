"""Response humanization endpoint."""

from fastapi import APIRouter, HTTPException, Depends
from app.models.requests import HumanizeRequest
from app.models.responses import HumanizeResponse
from app.core.humanizer import humanizer
from app.utils.validators import sanitize_text
from app.utils.logger import logger
from app.utils.auth import verify_api_key

router = APIRouter(prefix="/humanize", tags=["Humanization"])


@router.post("/response", response_model=HumanizeResponse, dependencies=[Depends(verify_api_key)])
async def humanize_response(request: HumanizeRequest):
    """Humanize an AI-generated response."""
    try:
        # Validate and sanitize input
        ai_response = sanitize_text(request.ai_response)
        if not ai_response:
            raise HTTPException(status_code=400, detail="Resposta não pode estar vazia")
        
        # Humanize response
        result = await humanizer.humanize(
            ai_response=ai_response,
            tone=request.tone,
            customer_sentiment=request.customer_sentiment,
            time_context=request.time_context
        )
        
        logger.info(f"Response humanized with tone: {result['tone_applied']}")
        
        return HumanizeResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in humanization endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao humanizar resposta")

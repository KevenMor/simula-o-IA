"""Simple Q&A endpoint using OpenAI only (no RAG)."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.core.llm_client import llm_client
from app.core.training_store import list_documents
from app.core.hallucination_checker import HallucinationChecker
from app.utils.validators import sanitize_text, validate_knowledge_base_id
from app.utils.logger import logger
from app.utils.auth import verify_api_key
from app.utils.cache import response_cache
from app.api.v1.settings import get_settings_file_path
from app.prompts.loader import load_tia_dani_petfriend
import json
import hashlib

TENANT_PETFRIEND = "hotel_creche_pet"


class QARequest(BaseModel):
    """Request model for simple Q&A."""

    question: str = Field(..., description="User question")
    tenant_id: Optional[str] = Field(
        None,
        description="Tenant/cliente (ex: autoescola_ideal). Se informado, usa os documentos de treinamento como contexto.",
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default_factory=list,
        description='Previous messages as a list of {"role": "...", "content": "..."}',
    )


class QAResponse(BaseModel):
    """Response model for simple Q&A."""

    answer: str = Field(..., description="Model answer")
    model_used: str = Field(..., description="LLM model used")
    confidence: Optional[float] = Field(None, description="Confidence score (0.0 to 1.0)")
    requires_human: bool = Field(False, description="Whether response should be reviewed by human")


router = APIRouter(prefix="/qa", tags=["Q&A"])

# Global hallucination checker
hallucination_checker = HallucinationChecker()


@router.post("/ask", response_model=QAResponse, dependencies=[Depends(verify_api_key)])
async def ask_question(request: QARequest) -> QAResponse:
    """Answer a question using the configured LLM (no vector DB)."""
    try:
        question = sanitize_text(request.question)
        if not question:
            raise HTTPException(status_code=400, detail="Pergunta não pode estar vazia")

        # Optional: load training docs for this tenant as context
        knowledge_context = ""
        context_hash = ""
        if request.tenant_id:
            if not validate_knowledge_base_id(request.tenant_id):
                raise HTTPException(status_code=400, detail="Tenant id invalido")
            docs = list_documents(request.tenant_id)
            if docs:
                # Concatenar conteudos, limitando para evitar estourar tokens
                # Reduzido para 18000 chars para economizar tokens
                parts: List[str] = []
                total_chars = 0
                for doc in docs:
                    chunk = doc.content or ""
                    if not chunk:
                        continue
                    if total_chars + len(chunk) > 18000:
                        break
                    parts.append(chunk)
                    total_chars += len(chunk)
                if parts:
                    knowledge_context = "\n\n---\n\n".join(parts)
                    # Hash do contexto para cache (se contexto mudar, cache invalida)
                    context_hash = hashlib.md5(knowledge_context.encode()).hexdigest()

        use_tia_dani = request.tenant_id == TENANT_PETFRIEND

        # Cache: pular para PetFriend (conversa depende do histórico)
        if not use_tia_dani:
            cached_response = response_cache.get(
                tenant_id=request.tenant_id or "default",
                question=question,
                context_hash=context_hash
            )
            if cached_response:
                return QAResponse(answer=cached_response, model_used=llm_client.default_model)

        # Build messages
        messages: List[Dict[str, str]] = []
        if request.conversation_history:
            messages.extend(request.conversation_history)

        user_content = question
        if knowledge_context:
            user_content = (
                "Contexto de conhecimento do cliente:\n"
                f"{knowledge_context}\n\n"
                f"Pergunta do cliente: {question}"
            )

        messages.append({"role": "user", "content": user_content})

        # System prompt: Tia Dani (PetFriend) ou padrão
        if use_tia_dani:
            system_prompt = load_tia_dani_petfriend()
        elif knowledge_context:
            system_prompt = (
                "Voce e um atendente humano virtual, falando em portugues brasileiro, "
                "no estilo de um atendente de WhatsApp de uma empresa amigavel. "
                "\n\n"
                "REGRAS CRITICAS - LEIA COM ATENCAO:\n"
                "1. Use APENAS e EXCLUSIVAMENTE as informacoes que estao no contexto fornecido.\n"
                "2. NUNCA invente, suponha ou crie informacoes que nao estejam explicitamente no contexto.\n"
                "3. Se a informacao NAO estiver no contexto, diga EXATAMENTE: 'Nao tenho essa informacao no momento, mas posso verificar com a equipe para voce. Pode me passar seu contato?'\n"
                "4. NUNCA use conhecimento geral ou suposicoes - APENAS o contexto fornecido.\n"
                "5. Se nao tiver certeza absoluta, prefira dizer que vai verificar do que inventar.\n"
                "\n"
                "TOMO E ESTILO:\n"
                "- Informal, caloroso e natural, como em uma conversa de WhatsApp\n"
                "- Curto e objetivo (2 a 4 frases)\n"
                "- Conduza a conversa para entender o que o cliente precisa\n"
                "- Evite frases de encerramento automaticas\n"
                "- Demonstre empatia quando o cliente estiver frustrado\n"
                "- Se ainda nao conhecer o nome do cliente, pergunte educadamente na primeira resposta\n"
                "\n"
                "LEMBRE-SE: E MELHOR DIZER 'NAO SEI' DO QUE INVENTAR INFORMACAO ERRADA."
            )
        else:
            # Sem contexto = só respostas genéricas
            system_prompt = (
                "Voce e um atendente humano virtual, falando em portugues brasileiro, "
                "no estilo de um atendente de WhatsApp de uma empresa amigavel. "
                "\n\n"
                "IMPORTANTE: Voce NAO tem acesso a informacoes especificas sobre a empresa neste momento. "
                "Portanto:\n"
                "1. Seja cordial e acolhedor\n"
                "2. Se o cliente perguntar algo especifico, diga: 'Nao tenho essa informacao agora, mas posso verificar com a equipe. Pode me passar seu contato?'\n"
                "3. NUNCA invente informacoes sobre precos, horarios, servicos, etc.\n"
                "4. Foque em coletar o nome do cliente e entender como pode ajudar\n"
            )

        # Carregar configurações do tenant (se disponível)
        tenant_settings = None
        if request.tenant_id:
            try:
                settings_file = get_settings_file_path()
                if settings_file.exists():
                    with open(settings_file, "r", encoding="utf-8") as f:
                        all_settings = json.load(f)
                        tenant_data = all_settings.get(request.tenant_id)
                        if tenant_data:
                            from app.api.v1.settings import TenantSettings
                            tenant_settings = TenantSettings(**tenant_data)
            except Exception as e:
                logger.warning(f"Error loading tenant settings: {e}")
        
        # Usar configurações do tenant ou padrões
        temperature = tenant_settings.temperature if tenant_settings else 0.3
        max_tokens = tenant_settings.max_tokens if tenant_settings else 1000
        confidence_threshold = tenant_settings.confidence_threshold if tenant_settings else 0.5
        enable_hallucination_check = tenant_settings.enable_hallucination_check if tenant_settings else True
        if use_tia_dani:
            enable_hallucination_check = False  # Tia Dani tem prompt específico; não sobrescrever
        
        # Gerar resposta com temperatura configurável
        answer = await llm_client.generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        # VALIDAÇÃO ANTI-ALUCINAÇÃO (se habilitada)
        is_valid = True
        confidence = 1.0
        validation_reason = ""
        requires_human = False
        
        if enable_hallucination_check:
            is_valid, confidence, validation_reason = await hallucination_checker.validate_response(
                question=question,
                answer=answer,
                knowledge_context=knowledge_context,
                has_context=bool(knowledge_context)
            )
            
            # Se confiança muito baixa ou inválida, substituir resposta
            if not is_valid or confidence < confidence_threshold:
                logger.warning(
                    f"Low confidence response detected (conf={confidence:.2f}, valid={is_valid}). "
                    f"Reason: {validation_reason}"
                )
                # Resposta segura quando detecta possível alucinação
                answer = (
                    "Desculpe, nao tenho certeza sobre essa informacao no momento. "
                    "Vou verificar com a equipe e retorno para voce. "
                    "Pode me passar seu nome e contato para eu te avisar quando tiver a resposta?"
                )
                requires_human = True
                confidence = 0.3  # Baixa confiança = precisa revisão humana
        
        # Cache (não usar para PetFriend)
        if not use_tia_dani:
            response_cache.set(
                tenant_id=request.tenant_id or "default",
                question=question,
                context_hash=context_hash,
                response=answer
            )

        return QAResponse(
            answer=answer,
            model_used=llm_client.default_model,
            confidence=confidence,
            requires_human=requires_human
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in QA endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao responder pergunta")


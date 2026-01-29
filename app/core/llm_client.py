"""LLM client for OpenAI and Anthropic."""

from typing import List, Dict, Optional
from openai import OpenAI
from app.config import settings
from app.utils.logger import logger


class LLMClient:
    """Client for interacting with LLM APIs."""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.default_model = settings.default_llm_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens
    
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate response using OpenAI API."""
        try:
            # Prepare messages
            formatted_messages = []
            if system_prompt:
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            formatted_messages.extend(messages)
            
            # Call OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=formatted_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def generate_with_context(
        self,
        user_query: str,
        context: List[str],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate response with RAG context."""
        # Build context string
        context_text = "\n\n".join([
            f"Fonte {i+1}: {ctx}" for i, ctx in enumerate(context)
        ])
        
        system_prompt = """Você é um assistente virtual especializado em atendimento ao cliente em português brasileiro.
Use as informações fornecidas no contexto para responder de forma precisa e útil.
Se a informação não estiver no contexto, seja honesto e diga que não tem essa informação.
Seja natural, empático e use linguagem apropriada para o contexto brasileiro."""
        
        # Build messages
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
        
        user_message = f"""Contexto relevante:
{context_text}

Pergunta do cliente: {user_query}

Responda de forma clara e útil, usando o contexto fornecido."""
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return await self.generate_response(
            messages=messages,
            system_prompt=system_prompt
        )


# Global instance
llm_client = LLMClient()

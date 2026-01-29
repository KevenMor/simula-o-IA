"""Hallucination detection and response validation."""

from typing import Tuple
from app.core.llm_client import llm_client
from app.utils.logger import logger


class HallucinationChecker:
    """Check if AI response contains hallucinations (made-up information)."""
    
    async def validate_response(
        self,
        question: str,
        answer: str,
        knowledge_context: str,
        has_context: bool = True
    ) -> Tuple[bool, float, str]:
        """Validate if response is based on context and not hallucinated.
        
        Returns:
            (is_valid, confidence_score, feedback)
        """
        if not has_context or not knowledge_context:
            # Sem contexto = sempre precisa passar para humano se for informação específica
            # Mas permite respostas genéricas (saudações, etc.)
            return self._check_generic_response(question, answer)
        
        # Verificar se a resposta está baseada no contexto
        validation_prompt = f"""Voce e um validador de respostas de IA. Sua tarefa e verificar se a resposta fornecida esta baseada APENAS no contexto fornecido, sem inventar informacoes.

CONTEXTO DISPONIVEL:
{knowledge_context[:5000]}

PERGUNTA DO CLIENTE:
{question}

RESPOSTA DA IA:
{answer}

INSTRUCOES:
1. Verifique se TODAS as informacoes na resposta estao presentes no contexto fornecido
2. Se a resposta menciona algo que NAO esta no contexto, isso e uma alucinacao
3. Se a resposta diz "nao sei" ou "preciso verificar", isso e VALIDO (nao e alucinacao)
4. Respostas genericas de atendimento (saudacoes, empatia) sao VALIDAS mesmo sem contexto especifico

Responda APENAS com um JSON no formato:
{{
    "is_valid": true/false,
    "confidence": 0.0 a 1.0,
    "reason": "explicacao curta"
}}

Seja RIGOROSO: qualquer informacao especifica que nao esteja no contexto = alucinacao."""

        try:
            validation_response = await llm_client.generate_response(
                messages=[{"role": "user", "content": validation_prompt}],
                system_prompt="Voce e um validador rigoroso. Responda APENAS com JSON valido.",
                temperature=0.1,  # Baixa temperatura para ser mais preciso
                max_tokens=200
            )
            
            # Parse JSON response
            import json
            import re
            
            # Extrair JSON da resposta
            json_match = re.search(r'\{[^}]+\}', validation_response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                is_valid = result.get("is_valid", False)
                confidence = float(result.get("confidence", 0.0))
                reason = result.get("reason", "")
                
                logger.info(
                    f"Hallucination check: valid={is_valid}, confidence={confidence:.2f}, reason={reason[:100]}"
                )
                
                return (is_valid, confidence, reason)
            else:
                # Se não conseguiu parsear, assume válido mas com baixa confiança
                logger.warning("Could not parse validation response, assuming valid with low confidence")
                return (True, 0.5, "Nao foi possivel validar automaticamente")
                
        except Exception as e:
            logger.error(f"Error in hallucination check: {e}")
            # Em caso de erro, assume válido mas loga
            return (True, 0.6, f"Erro na validacao: {str(e)}")
    
    def _check_generic_response(self, question: str, answer: str) -> Tuple[bool, float, str]:
        """Check if response is generic (greetings, empathy) and doesn't need context."""
        generic_phrases = [
            "oi", "ola", "bom dia", "boa tarde", "boa noite",
            "como posso ajudar", "entendo", "compreendo",
            "qual seu nome", "me chamo", "pode me chamar"
        ]
        
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # Se pergunta é genérica (saudação) e resposta também, é válido
        if any(phrase in question_lower for phrase in generic_phrases):
            if any(phrase in answer_lower for phrase in generic_phrases):
                return (True, 0.9, "Resposta generica valida")
        
        # Se resposta menciona "não sei" ou "verificar", é válido
        if any(phrase in answer_lower for phrase in ["nao sei", "nao tenho certeza", "preciso verificar", "vou consultar"]):
            return (True, 0.8, "Resposta honesta sobre falta de informacao")
        
        # Se não tem contexto e resposta parece específica, pode ser alucinação
        if len(answer) > 100 and not any(phrase in answer_lower for phrase in ["nao sei", "verificar", "consulta"]):
            return (False, 0.3, "Resposta especifica sem contexto - pode ser alucinacao")
        
        return (True, 0.7, "Resposta generica aceitavel")

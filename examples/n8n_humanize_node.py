#!/usr/bin/env python3
"""
Script Python para uso no n8n (Execute Command) - Humanização de resposta e tratamento de erros.

Uso no n8n:
- Node: Execute Command
- Command: python
- Arguments: /caminho/para/n8n_humanize_node.py
- Ou: python -c "$(cat n8n_humanize_node.py)"  (se receber input via stdin)

Input esperado (stdin ou variável de ambiente N8N_INPUT): JSON com:
  - response ou ai_response (texto a humanizar)
  - tone (opcional): "friendly" | "formal"
  - customer_sentiment (opcional): "negative" | "neutral" | "positive"
  - time_context (opcional): "morning" | "afternoon" | "evening"

Output (stdout): JSON com humanized_response, tone_applied, success, error (se houver).
Em caso de erro, retorna o texto original em humanized_response e success: false.
"""

import json
import re
import random
import sys
from datetime import datetime
from typing import Any, Dict, Optional

# --- Constantes (espelhando app/core/humanizer.py) ---
GREETINGS_MORNING = ["Bom dia", "Bom dia!", "Olá, bom dia"]
GREETINGS_AFTERNOON = ["Boa tarde", "Boa tarde!", "Olá, boa tarde"]
GREETINGS_EVENING = ["Boa noite", "Boa noite!", "Olá, boa noite"]
EMPATHY_PHRASES = [
    "Fico feliz em ajudar",
    "Entendo perfeitamente",
    "Claro, vou te ajudar",
    "Sem problemas",
]
CLOSING_PHRASES = [
    "Estou à disposição",
    "Qualquer dúvida, é só chamar",
    "Espero ter ajudado",
]
FRIENDLY_REPLACEMENTS = {
    "É necessário": "Precisa",
    "É preciso": "Precisa",
    "Deve-se": "Você pode",
    "Recomenda-se": "Recomendo",
}
FORMAL_REPLACEMENTS = {
    "Precisa": "É necessário",
    "Você pode": "É possível",
    "Recomendo": "Recomenda-se",
}
MAX_TEXT_LENGTH = 10000


def sanitize_text(text: str) -> str:
    """Limpa e trunca o texto."""
    if not text or not isinstance(text, str):
        return ""
    text = re.sub(r"\s+", " ", text.strip())
    return text[:MAX_TEXT_LENGTH] if len(text) > MAX_TEXT_LENGTH else text


def get_greeting(time_context: Optional[str]) -> Optional[str]:
    """Retorna saudação conforme horário."""
    if time_context in ("morning", "afternoon", "evening"):
        if time_context == "morning":
            return random.choice(GREETINGS_MORNING)
        if time_context == "afternoon":
            return random.choice(GREETINGS_AFTERNOON)
        return random.choice(GREETINGS_EVENING)
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return random.choice(GREETINGS_MORNING)
    if 12 <= hour < 18:
        return random.choice(GREETINGS_AFTERNOON)
    if 18 <= hour < 24:
        return random.choice(GREETINGS_EVENING)
    return None


def make_friendly(text: str) -> str:
    """Torna o texto mais amigável."""
    for formal, friendly in FRIENDLY_REPLACEMENTS.items():
        if formal in text:
            text = text.replace(formal, friendly, 1)
    return text


def make_formal(text: str) -> str:
    """Torna o texto mais formal."""
    for casual, formal in FORMAL_REPLACEMENTS.items():
        if casual in text:
            text = text.replace(casual, formal, 1)
    return text


def humanize(
    ai_response: str,
    tone: str = "friendly",
    customer_sentiment: Optional[str] = None,
    time_context: Optional[str] = None,
) -> str:
    """Aplica humanização ao texto (lógica autocontida)."""
    humanized = sanitize_text(ai_response)
    if not humanized:
        return ai_response if ai_response else ""

    greeting = get_greeting(time_context)
    if greeting:
        humanized = f"{greeting}! {humanized}"

    if customer_sentiment == "negative":
        empathy = random.choice(EMPATHY_PHRASES)
        if greeting:
            humanized = humanized.replace(f"{greeting}! ", f"{greeting}! {empathy}. ", 1)
        else:
            humanized = f"{empathy}. {humanized}"

    if tone == "friendly":
        humanized = make_friendly(humanized)
    elif tone == "formal":
        humanized = make_formal(humanized)

    if tone == "friendly" and customer_sentiment != "negative":
        emoji = random.choice(["😊", "👍", "✨"])
        if "!" in humanized[:20]:
            humanized = humanized.replace("!", f"! {emoji}", 1)
        else:
            humanized = f"{humanized} {emoji}"

    if len(humanized) > 100 and tone == "friendly":
        closing = random.choice(CLOSING_PHRASES)
        humanized = f"{humanized}\n\n{closing}!"

    return humanized


def read_input() -> Dict[str, Any]:
    """Lê o input: stdin (JSON) ou variável N8N_INPUT."""
    raw = None
    if not sys.stdin.isatty():
        raw = sys.stdin.read()
    if not raw and sys.argv and len(sys.argv) > 1:
        # n8n às vezes passa o JSON como primeiro argumento
        raw = sys.argv[1]
    if not raw:
        try:
            import os
            raw = os.environ.get("N8N_INPUT", "{}")
        except Exception:
            raw = "{}"
    try:
        return json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return {"ai_response": raw or ""}


def main() -> None:
    """Lê input, humaniza e imprime JSON no stdout. Nunca quebra o workflow."""
    result = {
        "humanized_response": "",
        "response": "",
        "tone_applied": "friendly",
        "success": False,
        "error": None,
    }
    try:
        data = read_input()

        # Aceita resposta do Process Message (response) ou do endpoint humanize (ai_response)
        text = data.get("response") or data.get("ai_response") or ""
        if isinstance(text, dict):
            text = text.get("response") or text.get("ai_response") or ""

        tone = (data.get("tone") or "friendly").strip().lower()
        if tone not in ("friendly", "formal"):
            tone = "friendly"
        customer_sentiment = data.get("customer_sentiment")
        time_context = data.get("time_context")

        if not text:
            result["humanized_response"] = ""
            result["response"] = ""
            result["success"] = True
            result["tone_applied"] = tone
            print(json.dumps(result, ensure_ascii=False))
            return

        humanized = humanize(
            ai_response=text,
            tone=tone,
            customer_sentiment=customer_sentiment,
            time_context=time_context,
        )

        result["humanized_response"] = humanized
        result["response"] = humanized  # n8n espera "response" para Send WhatsApp
        result["tone_applied"] = tone
        result["success"] = True
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        # Fallback: manter texto original se existir
        try:
            data = read_input()
            orig = data.get("response") or data.get("ai_response") or ""
            if isinstance(orig, dict):
                orig = orig.get("response") or orig.get("ai_response") or ""
            result["humanized_response"] = orig if isinstance(orig, str) else ""
            result["response"] = result["humanized_response"]
        except Exception:
            result["humanized_response"] = ""
            result["response"] = ""
        print(json.dumps(result, ensure_ascii=False))
        # Não re-raise: evita falha do workflow no n8n
        sys.exit(0)


if __name__ == "__main__":
    main()

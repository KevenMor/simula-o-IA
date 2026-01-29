"""Input validation utilities."""

import re
from typing import Optional


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """Sanitize and truncate text input for short fields.

    This version is aggressive: it colapsa quebras de linha e espacos
    sucessivos em um unico espaco. Use apenas para campos curtos
    (titulo, categoria etc.).
    """
    if not text:
        return ""

    # Remove excessive whitespace (including newlines)
    text = re.sub(r"\s+", " ", text.strip())

    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]

    return text


def sanitize_text_preserve_newlines(text: str, max_length: int = 100000) -> str:
    """Sanitize text but preservando quebras de linha (para Markdown, etc.).

    - Normaliza finais de linha para '\n'
    - Remove tabs e espacos repetidos, mas mantem '\n'
    - Trunca apenas por tamanho, sem alterar estrutura de paragrafo
    """
    if not text:
        return ""

    # Normalizar finais de linha
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Limpar espacos em excesso dentro das linhas, preservando '\n'
    lines = []
    for line in text.split("\n"):
        # Substitui multiplos espacos/tabs por um espaco simples
        cleaned = re.sub(r"[ \t]+", " ", line).rstrip()
        lines.append(cleaned)

    normalized = "\n".join(lines).strip()

    if len(normalized) > max_length:
        normalized = normalized[:max_length]

    return normalized


def validate_phone_number(phone: str) -> bool:
    """Validate Brazilian phone number format."""
    # Remove non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Brazilian phone: 10-11 digits (with area code)
    return 10 <= len(digits) <= 11


def validate_knowledge_base_id(kb_id: str) -> bool:
    """Validate knowledge base ID format."""
    # Alphanumeric, underscore, hyphen, max 100 chars
    return bool(re.match(r'^[a-zA-Z0-9_-]{1,100}$', kb_id))

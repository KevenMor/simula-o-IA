"""Loader de prompts com injeção de data/hora (Tia Bia, etc.)."""

from pathlib import Path
from datetime import datetime

# Diretório dos prompts
PROMPTS_DIR = Path(__file__).resolve().parent

MESES_PT = {
    1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
    5: "maio", 6: "junho", 7: "julho", 8: "agosto",
    9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro",
}


def _saudacao_por_periodo(dt: datetime) -> str:
    """Manhã 5–12, Tarde 12–18, Noite 18–5."""
    h = dt.hour
    if 5 <= h < 12:
        return "Ótimo dia"
    if 12 <= h < 18:
        return "Ótima tarde"
    return "Ótima noite"


def load_tia_dani_petfriend(now: datetime | None = None) -> str:
    """Carrega o prompt da Tia Bia e injeta data/saudação."""
    if now is None:
        now = datetime.now()
    path = PROMPTS_DIR / "tia_dani_petfriend.txt"
    text = path.read_text(encoding="utf-8")
    return text.replace("{{DATA_DIA}}", str(now.day)).replace(
        "{{DATA_MES}}", MESES_PT[now.month]
    ).replace("{{DATA_ANO}}", str(now.year)).replace(
        "{{SAUDACAO_PERIODO}}", _saudacao_por_periodo(now)
    )

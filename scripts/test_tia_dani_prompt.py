"""Testa o loader do prompt Tia Dani."""
from app.prompts.loader import load_tia_dani_petfriend

p = load_tia_dani_petfriend()
print("OK: prompt carregado,", len(p), "caracteres")
assert "Ótimo dia" in p or "Ótima tarde" in p or "Ótima noite" in p
assert "{{DATA_DIA}}" not in p and "{{DATA_MES}}" not in p
print("Placeholders substituídos corretamente.")

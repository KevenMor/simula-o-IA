"""Streamlit frontend for simple Q&A with the FastAPI backend.

This file is intentionally ASCII-only to avoid encoding issues on Windows.
"""

import os

import requests
from dotenv import load_dotenv
import streamlit as st


load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY_N8N = os.getenv("API_KEY_N8N", "")
DEFAULT_TENANT = os.getenv("DEFAULT_TENANT_ID", "autoescola_ideal")


st.set_page_config(page_title="AI Agent Q&A", layout="centered")

with st.sidebar:
    st.header("Configuracao do chat")
    tenant_id = st.text_input(
        "ID do cliente (tenant)",
        value=DEFAULT_TENANT,
        help="Exemplo: autoescola_ideal, pet_shop_bom_pata",
    )

st.title("AI Agent - QA simples")
st.write(
    "Interface simples para conversar com a IA usando o modelo da OpenAI e, "
    "quando disponivel, a base de treinamento do cliente."
)

if not API_KEY_N8N:
    st.warning(
        "Variavel de ambiente API_KEY_N8N nao encontrada. "
        "Defina no .env para que o Streamlit consiga chamar a API."
    )

if "history" not in st.session_state:
    st.session_state.history = []


def call_backend(question: str):
    """Call FastAPI backend Q&A endpoint."""
    url = f"{BACKEND_URL}/api/v1/qa/ask"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY_N8N,
    }
    payload = {
        "question": question,
        "tenant_id": tenant_id or None,
        "conversation_history": st.session_state.history,
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        if resp.status_code != 200:
            st.error(f"Erro da API ({resp.status_code}): {resp.text}")
            return None
        data = resp.json()
        return data.get("answer")
    except Exception as exc:
        st.error(f"Erro ao chamar backend: {exc}")
        return None


for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


prompt = st.chat_input("Digite sua pergunta em portugues...")
if prompt:
    # Mostrar pergunta do usuario
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamar backend
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            answer = call_backend(prompt)
        if answer is not None:
            st.markdown(answer)
            st.session_state.history.append({"role": "assistant", "content": answer})
        else:
            st.markdown("Nao consegui obter uma resposta da API.")


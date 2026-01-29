"""Pagina Streamlit para treinamento simples da IA (documentos por cliente).

Faz chamadas para os endpoints:
  - GET  /api/v1/training/documents?tenant_id=...
  - POST /api/v1/training/documents
"""

import os
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv
import streamlit as st


load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_KEY_N8N = os.getenv("API_KEY_N8N", "")

st.set_page_config(page_title="Treinamento IA", layout="wide")

st.title("Treinamento da IA (documentos base)")
st.write(
    "Cadastre textos que representam a base de conhecimento de cada cliente. "
    "Por enquanto, os dados sao salvos em um arquivo local (data/training_data.json)."
)

if not API_KEY_N8N:
    st.warning(
        "Variavel de ambiente API_KEY_N8N nao encontrada. "
        "Defina no .env para que esta pagina consiga chamar a API."
    )


def api_get_documents(tenant_id: str) -> List[Dict[str, Any]]:
    """Fetch training documents for a tenant from the backend."""
    if not tenant_id:
        return []

    try:
        resp = requests.get(
            f"{BACKEND_URL}/api/v1/training/documents",
            params={"tenant_id": tenant_id},
            headers={"X-API-Key": API_KEY_N8N},
            timeout=30,
        )
        if resp.status_code != 200:
            st.error(f"Erro ao buscar documentos: {resp.status_code} - {resp.text}")
            return []
        return resp.json()
    except Exception as exc:
        st.error(f"Erro ao chamar API de treinamento (GET): {exc}")
        return []


def api_save_document(
    tenant_id: str,
    title: str,
    category: str,
    content: str,
    doc_id: str | None = None,
) -> Dict[str, Any] | None:
    """Create or update a document via backend."""
    payload = {
        "tenant_id": tenant_id,
        "title": title,
        "category": category or "geral",
        "content": content,
    }
    if doc_id:
        payload["id"] = doc_id

    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/v1/training/documents",
            json=payload,
            headers={"X-API-Key": API_KEY_N8N},
            timeout=30,
        )
        if resp.status_code != 200:
            st.error(f"Erro ao salvar documento: {resp.status_code} - {resp.text}")
            return None
        return resp.json()
    except Exception as exc:
        st.error(f"Erro ao chamar API de treinamento (POST): {exc}")
        return None


def api_delete_document(tenant_id: str, doc_id: str) -> bool:
    """Delete a document via backend."""
    try:
        resp = requests.delete(
            f"{BACKEND_URL}/api/v1/training/documents/{doc_id}",
            params={"tenant_id": tenant_id},
            headers={"X-API-Key": API_KEY_N8N},
            timeout=30,
        )
        if resp.status_code != 200:
            st.error(f"Erro ao deletar documento: {resp.status_code} - {resp.text}")
            return False
        return True
    except Exception as exc:
        st.error(f"Erro ao chamar API de treinamento (DELETE): {exc}")
        return False


# --- Formulario lateral ---
with st.sidebar:
    st.header("Config do cliente")
    tenant_id = st.text_input(
        "ID do cliente (tenant)",
        value="autoescola_ideal",
        help="Use um identificador simples, ex: autoescola_ideal, pet_shop_bom_pata",
    )

    st.markdown("---")
    st.subheader("Novo documento / editar")

    if "editing_doc" not in st.session_state:
        st.session_state.editing_doc = None

    title = st.text_input("Titulo", value="")
    category = st.text_input("Categoria", value="geral")
    content = st.text_area("Conteudo (Markdown completo)", height=400)

    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("Salvar documento"):
            if not tenant_id:
                st.error("Informe o ID do cliente (tenant).")
            elif not title or not content:
                st.error("Titulo e conteudo sao obrigatorios.")
            else:
                saved = api_save_document(
                    tenant_id=tenant_id,
                    title=title,
                    category=category,
                    content=content,
                    doc_id=st.session_state.editing_doc.get("id")
                    if st.session_state.editing_doc
                    else None,
                )
                if saved:
                    st.success("Documento salvo com sucesso.")
                    st.session_state.editing_doc = None
                    st.rerun()

    with col_clear:
        if st.button("Limpar formulario"):
            st.session_state.editing_doc = None
            st.rerun()


# --- Lista de documentos ---
st.subheader("Documentos cadastrados")

if not tenant_id:
    st.info("Informe um ID de cliente na barra lateral para ver os documentos.")
else:
    docs = api_get_documents(tenant_id)

    if not docs:
        st.info("Nenhum documento cadastrado ainda para este cliente.")
    else:
        for doc in docs:
            with st.expander(f"{doc['title']}  (categoria: {doc['category']})"):
                st.write(doc["content"])
                st.caption(f"ID: {doc['id']}  | Atualizado em: {doc['updated_at']}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Editar", key=f"edit_{doc['id']}"):
                        # Preenche o formulario lateral com o documento selecionado
                        st.session_state.editing_doc = doc
                        st.rerun()
                with c2:
                    if st.button("Excluir", key=f"delete_{doc['id']}"):
                        ok = api_delete_document(tenant_id, doc["id"])
                        if ok:
                            st.success("Documento excluido.")
                            st.rerun()


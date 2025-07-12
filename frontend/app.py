# frontend/app.py

import streamlit as st
import pandas as pd
import requests
import os
import time

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente Analista com FastAPI", layout="wide")
st.title("🤖 Agente Analista de Dados")

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Reset manual da sessão
st.sidebar.markdown("## ⚡ Opções")
if st.sidebar.button("🔄 Novo Chat / Reset"):
    st.session_state["thread_id"] = None
    st.session_state["chat_history"] = []
    st.experimental_rerun()

uploaded_file = st.file_uploader("📂 Carregar ficheiro CSV", type=["csv"])

if uploaded_file:
    uploaded_file.seek(0)
    df = pd.read_csv(uploaded_file)

    uploaded_file.seek(0)
    file_bytes = uploaded_file.read()
    files = {'file': (uploaded_file.name, file_bytes, 'text/csv')}
    try:
        upload_response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=15)
        if upload_response.status_code == 200:
            st.success("✅ Ficheiro carregado com sucesso para o backend!")
            st.session_state["thread_id"] = None
            st.session_state["chat_history"] = []
        else:
            st.error(f"❌ Erro ao carregar ficheiro para o backend: {upload_response.status_code} - {upload_response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Erro ao enviar ficheiro para backend: {e}")
    st.dataframe(df)
    st.success("✅ Ficheiro carregado com sucesso!")

    st.markdown("---")
    st.subheader("🔁 Gerir Índice Vetorial")
    if st.button("🔄 Reindexar embeddings manualmente"):
        with st.spinner("A reindexar embeddings no backend..."):
            try:
                reindex_response = requests.post(f"{BACKEND_URL}/reindex", timeout=30)
                if reindex_response.status_code == 200:
                    result = reindex_response.json()
                    if result.get("status") == "success":
                        st.success("✅ Índice reindexado com sucesso!")
                        st.session_state["thread_id"] = None
                        st.session_state["chat_history"] = []
                    else:
                        st.error(f"⚠️ Erro ao reindexar: {result.get('message', 'Erro desconhecido.')}")
                else:
                    st.error(f"❌ Erro HTTP ao reindexar: {reindex_response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Falha na ligação ao backend: {e}")

# Exibe o histórico do chat tipo ChatGPT
for msg in st.session_state["chat_history"]:
    if msg["role"] == "user":
        st.markdown(f"**🧑 Tu:** {msg['content']}")
    else:
        st.markdown(f"**🤖 Agente:** {msg['content']}")

# Campo para pergunta no fundo
with st.form(key="chat_form", clear_on_submit=True):
    question = st.text_area("❓ Coloca uma pergunta sobre os dados:", key="user_input", height=80)
    submitted = st.form_submit_button("Enviar")
    if submitted and question:
        st.session_state["chat_history"].append({"role": "user", "content": question})
        with st.spinner("🧠 A consultar o backend..."):
            try:
                payload = {"question": question}
                if st.session_state["thread_id"]:
                    payload["thread_id"] = st.session_state["thread_id"]
                response = requests.post(f"{BACKEND_URL}/analyse", json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    # Atualiza thread_id na sessão
                    thread_id = data.get("thread_id")
                    if thread_id:
                        st.session_state["thread_id"] = thread_id

                    agent_answer = data.get("agent_answer") or ""
                    # Adiciona resposta ao histórico
                    st.session_state["chat_history"].append({"role": "agent", "content": agent_answer})
                    st.experimental_rerun()
                else:
                    st.error(f"❌ Erro ao consultar /analyse: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Erro de ligação ao backend (/analyse): {e}")

# (Opcional) Botão para mostrar histórico raw do backend
if st.session_state["thread_id"]:
    if st.sidebar.button("🔍 Mostrar histórico raw do backend"):
        hist = requests.get(f"{BACKEND_URL}/history/{st.session_state['thread_id']}", timeout=10)
        if hist.status_code == 200:
            st.sidebar.markdown("### Histórico Backend")
            st.sidebar.json(hist.json())

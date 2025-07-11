# frontend/app.py

import streamlit as st
import pandas as pd
import requests
import os
import time

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

st.set_page_config(page_title="Agente Analista com FastAPI", layout="wide")
st.title("🤖 Agente Analista de Dados")

# Upload de ficheiro CSV
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
        else:
            st.error(f"❌ Erro ao carregar ficheiro para o backend: {upload_response.status_code} - {upload_response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Erro ao enviar ficheiro para backend: {e}")

    st.dataframe(df)
    st.success("✅ Ficheiro carregado com sucesso!")

    # 🔄 Botão para reindexar embeddings manualmente
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
                    else:
                        st.error(f"⚠️ Erro ao reindexar: {result.get('message', 'Erro desconhecido.')}")
                else:
                    st.error(f"❌ Erro HTTP ao reindexar: {reindex_response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Falha na ligação ao backend: {e}")

# Campo para pergunta
question = st.text_area("❓ Coloca uma pergunta sobre os dados:")

if question:
    with st.spinner("🧠 A consultar o backend..."):
        try:
            start = time.time()
            response = requests.post(f"{BACKEND_URL}/analyse", json={"question": question}, timeout=60)
            duration = time.time() - start

            if response.status_code == 200:
                data = response.json()
                query_answer = data.get("query_answer")
                agent_answer = data.get("agent_answer")

                st.subheader("📊 Resposta baseada nos dados:")
                if query_answer:
                    split_tag = "Context information is below."
                    if split_tag in query_answer:
                        query_answer = query_answer.split(split_tag)[-1].strip()
                    st.markdown(query_answer)
                else:
                    st.warning("Nenhuma resposta da consulta ao índice.")

                with st.expander("💬 Resposta geral do agente (LangChain)", expanded=False):
                    if agent_answer:
                        if agent_answer.startswith("iVBORw0KGgoAAAAN"):
                            st.image(f"data:image/png;base64,{agent_answer}")
                        else:
                            st.markdown(agent_answer)
                    else:
                        st.warning("Nenhuma resposta do agente.")
                
                st.caption(f"⏱️ Tempo de resposta total: {duration:.2f} segundos")

            else:
                st.error(f"❌ Erro ao consultar /analyse: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"⚠️ Erro de ligação ao backend (/analyse): {e}")

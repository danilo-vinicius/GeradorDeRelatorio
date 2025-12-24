import streamlit as st
import os

# Importação dos módulos
from modules import lpr, visita, faturamento, manutencao, parecer

# Configuração
st.set_page_config(page_title="Gerador de Relatórios Brasfort", page_icon="📄", layout="wide")

# --- MENU LATERAL ---
with st.sidebar:
    st.image("assets/logo.png", width=200)
    st.title("Menu")

    tipo_relatorio = st.selectbox(
        "Selecione o Relatório:",
        [
            "Selecione...",
            "Relatório de Manutenção",
            "Relatório para Faturamento",
            "Visita Técnica",
            "Parecer Técnico",
            "Incidente LPR (Acesso)"
        ]
    )
    st.info("Sistema v2.0 - Foco em Textualização")

# --- ROTEAMENTO ---
if tipo_relatorio == "Selecione...":
    st.title("Gerador de Relatórios 📄")
    st.write("Selecione um módulo no menu lateral para começar.")

elif tipo_relatorio == "Relatório de Manutenção":
    manutencao.renderizar_formulario_manutencao()

elif tipo_relatorio == "Relatório para Faturamento":
    faturamento.renderizar_formulario_faturamento()

elif tipo_relatorio == "Visita Técnica":
    visita.renderizar_formulario_visita()

elif tipo_relatorio == "Parecer Técnico":
    parecer.renderizar_formulario_parecer()

elif tipo_relatorio == "Incidente LPR (Acesso)":
    lpr.renderizar_formulario_lpr()
import streamlit as st
# Importando módulos
from modules import lpr
from modules import equipamento
from modules import visita  # <--- NOVO IMPORT
from modules import faturamento
from modules import manutencao
from modules import parecer

st.set_page_config(page_title="Gerador de Relatórios Brasfort", page_icon="📝")
st.title("📝 Sistema de Relatórios Técnicos")

st.sidebar.image("assets/logo.png", use_container_width=True) # Se tiver o logo já mostra no menu
st.sidebar.title("Menu de Opções")

tipo_relatorio = st.sidebar.selectbox(
    "Selecione o Relatório:",
    ["Ocorrência LPR", "Avaria de Equipamento", "Visita Técnica", "Faturamento", "Manutenção", "Parecer"]
)

# Inicializa estado
if "arquivo_gerado" not in st.session_state:
    st.session_state.arquivo_gerado = None

# Roteador de Telas
if tipo_relatorio == "Ocorrência LPR":
    lpr.renderizar_formulario_lpr()

elif tipo_relatorio == "Avaria de Equipamento":
    equipamento.renderizar_formulario_equipamento()

elif tipo_relatorio == "Visita Técnica":
    visita.renderizar_formulario_visita()

elif tipo_relatorio == "Faturamento":
    faturamento.renderizar_formulario_faturamento()

elif tipo_relatorio == "Manutenção":
    manutencao.renderizar_formulario_manutencao()

elif tipo_relatorio == "Parecer":
    parecer.renderizar_formulario_parecer()

# Botão de Download Global
st.divider()
if st.session_state.arquivo_gerado:
    st.success(f"Arquivo pronto: {st.session_state.arquivo_gerado}")
    with open(st.session_state.arquivo_gerado, "rb") as f:
        st.download_button(
            label="📄 Baixar PDF Finalizado",
            data=f,
            file_name=st.session_state.arquivo_gerado,
            mime="application/pdf"
        )
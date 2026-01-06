import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

def exibir_pdf_na_tela(caminho_arquivo):
    """
    Exibe o PDF usando um componente nativo que não é bloqueado pelo Chrome.
    """
    try:
        # Lê o arquivo como binário
        with open(caminho_arquivo, "rb") as f:
            pdf_bytes = f.read()
            
        # Exibe o PDF (width ajusta à largura da coluna automaticamente)
        # resolution_boost melhora a nitidez do texto
        pdf_viewer(input=pdf_bytes, width=700, height=800, resolution_boost=2)
        
    except Exception as e:
        st.error(f"Erro ao visualizar PDF: {e}")
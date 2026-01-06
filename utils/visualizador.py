import streamlit as st
import base64

def exibir_pdf_na_tela(caminho_arquivo):
    """
    Lê um arquivo PDF do disco e exibe em um iframe HTML dentro do Streamlit.
    """
    with open(caminho_arquivo, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    # Cria o HTML do visualizador (Iframe)
    # height="800" define a altura da janela
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
    
    st.markdown(pdf_display, unsafe_allow_html=True)
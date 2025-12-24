import streamlit as st
import os
from motor_relatorio import gerar_relatorio_lpr

# Configuração da Página
st.set_page_config(page_title="Gerador de Relatórios", page_icon="📝")

st.title("📝 Gerador de Relatórios Operacionais")
st.markdown("Preencha os dados abaixo para gerar o PDF da ocorrência.")

# --- INICIALIZAÇÃO DE ESTADO (MEMÓRIA) ---
# Isso impede que o botão de download suma quando você clicar nele
if "arquivo_gerado" not in st.session_state:
    st.session_state.arquivo_gerado = None

# --- SEÇÃO 1: DADOS GERAIS ---
st.header("1. Dados da Ocorrência")
col1, col2 = st.columns(2)

with col1:
    cliente = st.text_input("Nome do Cliente", value="Condomínio Cerejeiras")
    placa = st.text_input("Placa do Veículo", value="ABC-1234")

with col2:
    data_input = st.date_input("Data do Evento")
    data_formatada = data_input.strftime("%d/%m/%Y")

# --- SEÇÃO 2: HORÁRIOS ---
st.header("2. Análise Temporal")
st.caption("Digite os horários no formato HH:MM:SS (Ex: 14:10:05)")
col_h1, col_h2, col_h3 = st.columns(3)

with col_h1:
    h_chegada = st.text_input("Hora Chegada", value="14:10:05")
with col_h2:
    h_leitura = st.text_input("Hora Leitura LPR", value="14:10:15")
with col_h3:
    h_abertura = st.text_input("Hora Abertura Portão", value="14:10:25")

# --- SEÇÃO 3: EVIDÊNCIAS ---
st.header("3. Imagens")
st.info("Faça o upload das capturas de tela.")

def salvar_upload(arquivo_upload, nome_destino):
    if arquivo_upload is not None:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        caminho_completo = os.path.join("temp", nome_destino)
        with open(caminho_completo, "wb") as f:
            f.write(arquivo_upload.getbuffer())
        return caminho_completo
    return None

file_chegada = st.file_uploader("Foto 1: Chegada do Veículo (temp_chegada)", type=['jpg', 'png', 'jpeg'])
file_leitura = st.file_uploader("Foto 2: Leitura da Placa (temp_leitura)", type=['jpg', 'png', 'jpeg'])
file_abertura = st.file_uploader("Foto 3: Abertura do Portão (temp_abertura)", type=['jpg', 'png', 'jpeg'])

# --- BOTÃO DE GERAÇÃO ---
st.divider()

# Adicionei uma chave única (key) só por segurança
if st.button("Gerar Relatório PDF", type="primary", key="btn_gerar"):
    
    with st.spinner('Gerando documento...'):
        # 1. Salvar as imagens
        path_chegada = salvar_upload(file_chegada, "temp_chegada.jpg")
        path_leitura = salvar_upload(file_leitura, "temp_leitura.jpg")
        path_abertura = salvar_upload(file_abertura, "temp_abertura.jpg")

        # 2. Montar dados
        dados = {
            "cliente": cliente,
            "data": data_formatada,
            "placa": placa,
            "hora_chegada": h_chegada,
            "hora_leitura": h_leitura,
            "hora_abertura": h_abertura,
            "img_chegada": path_chegada if path_chegada else "",
            "img_leitura": path_leitura if path_leitura else "",
            "img_abertura": path_abertura if path_abertura else ""
        }

        # 3. Gerar e salvar na memória da sessão
        try:
            nome_arquivo = gerar_relatorio_lpr(dados)
            st.session_state.arquivo_gerado = nome_arquivo
            st.success("Relatório gerado com sucesso! Clique abaixo para baixar.")
        except Exception as e:
            st.error(f"Erro ao gerar: {e}")

# --- ÁREA DE DOWNLOAD (Fora do botão 'Gerar') ---
if st.session_state.arquivo_gerado:
    st.markdown("### 📥 Seu arquivo está pronto:")
    with open(st.session_state.arquivo_gerado, "rb") as f:
        st.download_button(
            label="Baixar PDF Agora",
            data=f,
            file_name=st.session_state.arquivo_gerado,
            mime="application/pdf",
            key="btn_download"  # Chave única para evitar conflito
        )
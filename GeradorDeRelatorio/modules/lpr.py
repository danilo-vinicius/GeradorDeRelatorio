import streamlit as st
import os
from datetime import datetime
# Importa a classe base que criamos
from utils.brasfort_pdf import RelatorioBrasfort

# --- FUNÇÃO AUXILIAR ---
def calcular_tempo(inicio_str, fim_str):
    try:
        formato = "%H:%M:%S"
        t_inicio = datetime.strptime(inicio_str, formato)
        t_fim = datetime.strptime(fim_str, formato)
        delta = t_fim - t_inicio
        return str(delta)
    except:
        return "Erro"

# --- MOTOR DE GERAÇÃO DO PDF ---
def gerar_relatorio_lpr(dados):
    # Passamos o título direto na criação da classe para evitar sobreposição
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE OCORRÊNCIA - LPR")
    pdf.add_page()
    
    # --- DADOS DO CLIENTE ---
    # Começamos um pouco mais para baixo (Y=30) para não bater no cabeçalho
    pdf.set_y(30) 
    
    pdf.set_x(10)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 6, f"Data da Ocorrência: {dados['data']}", ln=True)
    pdf.cell(0, 6, f"Placa do Veículo: {dados['placa']}", ln=True)
    pdf.ln(5)

    # --- 1. DETALHES ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Detalhes da Ocorrência", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    texto_intro = (
        f"Foi identificada uma falha no processo de leitura e autorização de acesso "
        f"do veículo de placa {dados['placa']}. Segue abaixo a análise temporal e evidências do sistema."
    )
    pdf.multi_cell(0, 6, texto_intro)
    pdf.ln(5)

    # --- 2. ANÁLISE TEMPORAL ---
    tempo_total = calcular_tempo(dados['hora_chegada'], dados['hora_abertura'])
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Barlow', 'B', 11)
    pdf.cell(0, 8, "2. Análise de Tempos (Logs do Sistema)", ln=True, fill=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.ln(2)
    pdf.cell(40, 8, "Chegada na Câmera:", border='B')
    pdf.cell(30, 8, dados['hora_chegada'], ln=True)
    
    pdf.cell(40, 8, "Leitura (OCR):", border='B')
    pdf.cell(30, 8, dados['hora_leitura'], ln=True)
    
    pdf.cell(40, 8, "Abertura Portão:", border='B')
    pdf.cell(30, 8, dados['hora_abertura'], ln=True)
    pdf.ln(5)

    pdf.set_text_color(200, 0, 0)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 10, f"Tempo Total de Processamento: {tempo_total}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Barlow', '', 11)
    pdf.ln(5)

    # --- 3. EVIDÊNCIAS ---
    pdf.set_font('Barlow', 'B', 11)
    pdf.cell(0, 8, "3. Evidências Visuais", ln=True, fill=True)
    pdf.ln(5)
    
    lista_imgs = [
        ("Registro de Chegada", dados['img_chegada']),
        ("Momento da Leitura", dados['img_leitura']),
        ("Acionamento do Portão", dados['img_abertura'])
    ]

    for titulo, caminho_img in lista_imgs:
        if caminho_img and os.path.exists(caminho_img):
            if pdf.get_y() > 220: pdf.add_page()
            
            pdf.set_font('Barlow', 'I', 10)
            pdf.cell(0, 6, titulo, ln=True)
            pdf.image(caminho_img, x=15, w=110) 
            pdf.ln(5)

    pdf.bloco_assinatura("Técnico Responsável / Operador")

    nome_arquivo = f"Relatorio_LPR_{dados['placa']}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE (FORMULÁRIO) ---
def renderizar_formulario_lpr():
    st.subheader("🚗 Ocorrência de Acesso (LPR)")
    st.caption("Preencha os dados da falha ou lentidão na leitura.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Nome do Cliente", value="Condomínio Cerejeiras")
        placa = st.text_input("Placa do Veículo", value="ABC-1234")
    with col2:
        data_input = st.date_input("Data do Evento")
        data_formatada = data_input.strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("**Horários (HH:MM:SS)**")
    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        h_chegada = st.text_input("Chegada", value="14:10:05")
    with col_h2:
        h_leitura = st.text_input("Leitura", value="14:10:15")
    with col_h3:
        h_abertura = st.text_input("Abertura", value="14:10:25")

    st.markdown("---")
    file_chegada = st.file_uploader("Foto 1: Chegada", type=['jpg', 'png'])
    file_leitura = st.file_uploader("Foto 2: Leitura", type=['jpg', 'png'])
    file_abertura = st.file_uploader("Foto 3: Abertura", type=['jpg', 'png'])

    if st.button("Gerar Relatório LPR", type="primary"):
        # Função interna para salvar imagem temporária
        def salvar_temp(arquivo, nome):
            if arquivo:
                if not os.path.exists("temp"): os.makedirs("temp")
                caminho = os.path.join("temp", nome)
                with open(caminho, "wb") as f:
                    f.write(arquivo.getbuffer())
                return caminho
            return ""

        path_chegada = salvar_temp(file_chegada, "lpr_chegada.jpg")
        path_leitura = salvar_temp(file_leitura, "lpr_leitura.jpg")
        path_abertura = salvar_temp(file_abertura, "lpr_abertura.jpg")

        dados = {
            "cliente": cliente,
            "data": data_formatada,
            "placa": placa,
            "hora_chegada": h_chegada,
            "hora_leitura": h_leitura,
            "hora_abertura": h_abertura,
            "img_chegada": path_chegada,
            "img_leitura": path_leitura,
            "img_abertura": path_abertura
        }

        try:
            arquivo = gerar_relatorio_lpr(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Relatório LPR gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
import streamlit as st
import os
from datetime import datetime
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

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

# --- MOTOR PDF ---
def gerar_relatorio_lpr(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE OCORRÊNCIA - LPR")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Incidente de Controle de Acesso (LPR)",
        sub_titulo=f"Veículo: {dados['placa']}\nLocal: {dados['cliente']}",
        autor=dados['operador']
    )
    
    pdf.add_page()
    
    # Cabeçalho Interno
    pdf.set_y(30)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 6, f"Placa do Veículo: {dados['placa']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Ocorrência: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. CONTEXTO (IA) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Descrição da Ocorrência", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['contexto'], align='J')
    pdf.ln(5)

    # --- 2. ANÁLISE TEMPORAL ---
    tempo_total = calcular_tempo(dados['hora_chegada'], dados['hora_abertura'])
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Análise de Logs do Sistema (Tempos)", ln=True, fill=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.ln(2)
    
    # Tabela simples
    pdf.cell(40, 8, "Chegada (Câmera):", border='B')
    pdf.cell(30, 8, dados['hora_chegada'], ln=True)
    
    pdf.cell(40, 8, "Leitura (OCR):", border='B')
    pdf.cell(30, 8, dados['hora_leitura'], ln=True)
    
    pdf.cell(40, 8, "Abertura Portão:", border='B')
    pdf.cell(30, 8, dados['hora_abertura'], ln=True)
    pdf.ln(5)
    
    # Destaque Vermelho
    pdf.set_text_color(200, 0, 0)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 10, f"Tempo Total de Processamento: {tempo_total}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Barlow', '', 11)
    
    # Explicação Técnica da Falha (IA)
    if dados['analise_tecnica']:
        pdf.ln(2)
        pdf.multi_cell(0, 6, dados['analise_tecnica'], align='J')
    pdf.ln(5)

    # --- 3. EVIDÊNCIAS ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. Evidências Visuais", ln=True)
    pdf.ln(2)
    
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
            try:
                pdf.image(caminho_img, x=15, w=110)
            except:
                pdf.cell(0, 6, "[Erro na imagem]", ln=True)
            pdf.ln(5)

    # --- 4. CONCLUSÃO ---
    if dados['conclusao']:
        if pdf.get_y() > 240: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "4. Conclusão e Providências", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['conclusao'], align='J')
        pdf.ln(5)

    pdf.bloco_assinatura(dados['operador'])

    nome_arquivo = f"LPR_{dados['placa']}_{dados['cliente'].split()[0]}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_lpr():
    st.subheader("🚗 Incidente de Acesso (LPR)")
    st.caption("Relatório detalhado de falhas de leitura ou acesso.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Nome do Cliente", value="Condomínio Cerejeiras")
        placa = st.text_input("Placa do Veículo", value="ABC-1234")
    with col2:
        operador = st.text_input("Operador/Técnico", value="Monitoramento")
        data_input = st.date_input("Data do Evento")
        data_formatada = data_input.strftime("%d/%m/%Y")

    st.markdown("---")
    
    # --- 1. CONTEXTO (IA) ---
    st.write("### 1. O que aconteceu? (Contexto)")
    if "txt_lpr_contexto" not in st.session_state: st.session_state.txt_lpr_contexto = ""
    
    rascunho_ctx = st.text_area("Relato da ocorrência:", 
                               placeholder="Ex: O morador do 302 reclamou que ficou parado 1 minuto e o portão não abriu...", height=60)
    
    if st.button("Formalizar Relato", key="btn_lpr_ctx", type="secondary"):
        prompt = "Formalize este relato de ocorrência de portaria/controle de acesso."
        st.session_state.txt_lpr_contexto = melhorar_texto_com_ia(rascunho_ctx + ". " + prompt, "Ocorrência LPR")
        
    contexto_final = st.text_area("Texto Final Contexto:", value=st.session_state.txt_lpr_contexto, height=100)

    # --- 2. ANÁLISE TÉCNICA E HORÁRIOS ---
    st.write("### 2. Análise Técnica")
    
    c_h1, c_h2, c_h3 = st.columns(3)
    with c_h1: h_chegada = st.text_input("Chegada (HH:MM:SS)", value="14:10:05")
    with c_h2: h_leitura = st.text_input("Leitura (HH:MM:SS)", value="14:10:15")
    with c_h3: h_abertura = st.text_input("Abertura (HH:MM:SS)", value="14:10:25")

    if "txt_lpr_analise" not in st.session_state: st.session_state.txt_lpr_analise = ""
    
    rascunho_analise = st.text_area("Por que demorou/falhou?", 
                                   placeholder="Ex: O sol estava batendo na placa causando reflexo. Ou: A internet caiu.", height=60)
    
    if st.button("Formalizar Análise", key="btn_lpr_ana", type="secondary"):
        prompt = "Explique tecnicamente a causa provável dessa falha de leitura LPR."
        st.session_state.txt_lpr_analise = melhorar_texto_com_ia(rascunho_analise + ". " + prompt, "Análise Técnica LPR")
        
    analise_final = st.text_area("Texto Final Análise:", value=st.session_state.txt_lpr_analise, height=80)

    # --- 3. FOTOS ---
    st.write("### 3. Evidências")
    f1 = st.file_uploader("Foto 1: Chegada", type=['jpg', 'png'])
    f2 = st.file_uploader("Foto 2: Leitura", type=['jpg', 'png'])
    f3 = st.file_uploader("Foto 3: Abertura", type=['jpg', 'png'])

    # --- 4. CONCLUSÃO (IA) ---
    st.write("### 4. Conclusão")
    if "txt_lpr_conclusao" not in st.session_state: st.session_state.txt_lpr_conclusao = ""
    
    rascunho_conc = st.text_area("O que foi feito?", placeholder="Ex: Liberado manualmente e aberto chamado pra ajustar a câmera.", height=60)
    
    if st.button("Formalizar Conclusão", key="btn_lpr_conc", type="secondary"):
        st.session_state.txt_lpr_conclusao = melhorar_texto_com_ia(rascunho_conc, "Conclusão LPR")
        
    conclusao_final = st.text_area("Texto Final Conclusão:", value=st.session_state.txt_lpr_conclusao, height=80)

    if st.button("Gerar Relatório LPR", type="primary"):
        # Função interna para salvar imagem temporária
        def salvar_temp(arquivo, nome):
            if arquivo:
                if not os.path.exists("temp"): os.makedirs("temp")
                caminho = os.path.join("temp", nome)
                with open(caminho, "wb") as f: f.write(arquivo.getbuffer())
                return caminho
            return ""

        dados = {
            "cliente": cliente,
            "data": data_formatada,
            "placa": placa,
            "operador": operador,
            "contexto": contexto_final,
            "hora_chegada": h_chegada,
            "hora_leitura": h_leitura,
            "hora_abertura": h_abertura,
            "analise_tecnica": analise_final,
            "conclusao": conclusao_final,
            "img_chegada": salvar_temp(f1, "lpr_1.jpg"),
            "img_leitura": salvar_temp(f2, "lpr_2.jpg"),
            "img_abertura": salvar_temp(f3, "lpr_3.jpg")
        }

        try:
            arquivo = gerar_relatorio_lpr(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Relatório LPR gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
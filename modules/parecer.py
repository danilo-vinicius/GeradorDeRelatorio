import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_parecer(dados):
    # Título de peso
    pdf = RelatorioBrasfort(titulo="PARECER TÉCNICO DE ENGENHARIA")
    
    # Capa com título formal
    pdf.gerar_capa(
        titulo_principal="Parecer Técnico",
        sub_titulo=f"Assunto: {dados['assunto']}\nCliente: {dados['cliente']}",
        autor=dados['responsavel']
    )
    
    pdf.add_page()
    
    # --- CABEÇALHO DO DOCUMENTO ---
    pdf.set_y(30)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Referência: {dados['assunto']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Emissão: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. OBJETO DA ANÁLISE ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Objeto da Análise", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['objeto'])
    pdf.ln(5)

    # --- 2. ANÁLISE TÉCNICA E CONSTATAÇÕES ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Análise Técnica e Constatações", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['analise'])
    pdf.ln(5)

    # --- 3. EMBASAMENTO / NORMAS (Opcional) ---
    if dados['embasamento']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. Embasamento Técnico / Normativo", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['embasamento'])
        pdf.ln(5)

    # --- 4. CONCLUSÃO E PARECER FINAL ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. Conclusão e Parecer Final", ln=True)
    
    # Caixa de destaque para a conclusão
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Barlow', '', 11)
    # Salva posição Y
    y_inicio = pdf.get_y()
    # Escreve o texto para medir a altura
    pdf.multi_cell(0, 6, dados['conclusao'])
    # Desenha borda/fundo (simplificado: desenhamos um retângulo cinza antes se soubéssemos a altura, 
    # ou apenas deixamos o texto limpo para evitar complexidade de cálculo de altura no FPDF)
    
    pdf.ln(10)

    # --- ASSINATURA ---
    pdf.bloco_assinatura(dados['responsavel'])
    
    nome_arquivo = f"Parecer_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_parecer():
    st.subheader("⚖️ Parecer Técnico / Laudo Pericial")
    st.caption("Documento formal para análise de causas, incidentes e validação técnica.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Solar")
        assunto = st.text_input("Assunto/Título", value="Análise de Queima por Descarga Atmosférica")
    with col2:
        responsavel = st.text_input("Responsável Técnico", value="Eng. Fulano de Tal")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")
    
    # 1. O Objeto
    st.write("**1. O que foi analisado? (Objeto)**")
    objeto = st.text_area("Descreva o equipamento ou cenário analisado:", height=70,
                         value="Sistema de CFTV e Central de Alarme do Bloco B, após incidente de energia.")

    # 2. A Análise (Com IA)
    st.write("**2. Análise Técnica (O que você viu?)**")
    
    if "texto_parecer_analise" not in st.session_state:
        st.session_state.texto_parecer_analise = ""

    rascunho_analise = st.text_area("Rascunho da Análise:", 
                                   placeholder="Ex: Medi a tensão e tava 220v onde devia ser 12v. O varistor torrou...",
                                   height=100)

    if st.button("✨ Melhorar Análise (IA)", key="btn_ia_analise", type="secondary"):
        if len(rascunho_analise) > 5:
            with st.spinner("Consultando normas e redigindo análise..."):
                # Prompt específico para pedir normas técnicas
                prompt_extra = "Inclua termos técnicos e, se possível, cite que os danos são compatíveis com sobretensão elétrica."
                texto = melhorar_texto_com_ia(rascunho_analise + ". " + prompt_extra, "Parecer Técnico de Engenharia")
                st.session_state.texto_parecer_analise = texto

    analise_final = st.text_area("Texto Final da Análise:", value=st.session_state.texto_parecer_analise, height=150)

    # 3. Conclusão
    st.write("**3. Conclusão Final**")
    conclusao = st.text_area("Veredito:", height=100, 
                            placeholder="Ex: Conclui-se que a queima foi causada por fator externo (raio), não coberto pela garantia.")

    if st.button("Gerar Parecer Técnico", type="primary"):
        dados = {
            "cliente": cliente,
            "assunto": assunto,
            "responsavel": responsavel,
            "data": data,
            "objeto": objeto,
            "analise": analise_final,
            "embasamento": "", # Deixei opcional para simplificar, ou a IA pode gerar junto na análise
            "conclusao": conclusao
        }

        try:
            arquivo = gerar_pdf_parecer(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Parecer gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
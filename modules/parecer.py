import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_parecer(dados):
    pdf = RelatorioBrasfort(titulo="PARECER TÉCNICO DE ENGENHARIA")
    
    pdf.gerar_capa(
        titulo_principal="Parecer Técnico",
        sub_titulo=f"Assunto: {dados['assunto']}\nCliente: {dados['cliente']}",
        autor=dados['responsavel']
    )
    
    pdf.add_page()
    
    # Cabeçalho Interno
    pdf.set_y(30)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Referência: {dados['assunto']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Emissão: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. HISTÓRICO (INTRODUÇÃO) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Histórico e Contexto", ln=True)
    pdf.set_font('Barlow', '', 11)
    # align='J' deixa o texto justificado (reto nas duas margens)
    pdf.multi_cell(0, 6, dados['historico'], align='J') 
    pdf.ln(5)

    # --- 2. METODOLOGIA (NOVO) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Metodologia de Análise", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['metodologia'], align='J')
    pdf.ln(5)

    # --- 3. ANÁLISE TÉCNICA (DESENVOLVIMENTO) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. Análise Técnica e Constatações", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['analise'], align='J')
    pdf.ln(5)

    # --- 4. CONCLUSÃO (DESFECHO) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. Conclusão e Parecer Final", ln=True)
    
    # Caixa cinza para destaque do veredito
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Barlow', '', 11)
    
    # Truque para desenhar retângulo em volta de texto multi_cell é complexo no FPDF,
    # então vamos fazer apenas o texto com fundo se for curto, ou normal se longo.
    # Aqui vou deixar normal justificado para garantir limpeza.
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    # Assinatura
    pdf.bloco_assinatura(dados['responsavel'])
    
    nome_arquivo = f"Parecer_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_parecer():
    st.subheader("⚖️ Parecer Técnico (Estruturado)")
    st.caption("Preencha as etapas para compor um laudo completo.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Solar")
        assunto = st.text_input("Assunto", value="Queima de Central de Alarme")
    with col2:
        responsavel = st.text_input("Responsável Técnico", value="Eng. Técnico Brasfort")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- ETAPA 1: HISTÓRICO (Onde a IA ajuda a formalizar a queixa) ---
    st.write("### 1. Histórico (Introdução)")
    if "txt_historico" not in st.session_state: st.session_state.txt_historico = ""
    
    rascunho_hist = st.text_area("O que aconteceu? (Relato do cliente)", 
                                placeholder="Ex: O zelador informou que terça feira deu um raio e parou tudo...", height=70)
    
    if st.button("Formalizar Histórico", key="btn_hist"):
        prompt = "Reescreva como uma introdução formal de relatório técnico, citando a solicitação do cliente."
        st.session_state.txt_historico = melhorar_texto_com_ia(rascunho_hist + ". " + prompt, "Histórico")
    
    hist_final = st.text_area("Texto Final Histórico:", value=st.session_state.txt_historico, height=100)

    # --- ETAPA 2: METODOLOGIA (Sugestão Automática) ---
    st.write("### 2. Metodologia (Como você testou?)")
    metodologia_padrao = "Foi realizada inspeção visual dos componentes, seguida de medição das tensões de entrada e saída com multímetro True-RMS, além da análise dos logs de eventos do sistema."
    metodologia = st.text_area("Descreva os testes:", value=metodologia_padrao, height=70)

    # --- ETAPA 3: ANÁLISE (O coração do laudo) ---
    st.write("### 3. Análise Técnica (O que você achou?)")
    if "txt_analise" not in st.session_state: st.session_state.txt_analise = ""
    
    rascunho_analise = st.text_area("Seus achados técnicos:", 
                                   placeholder="Ex: A placa fonte tá preta, varistor estourado. Medi a tomada e ta oscilando.", height=100)
    
    if st.button("Gerar Análise Técnica", key="btn_analise"):
        prompt = "Descreva tecnicamente os danos, citando componentes eletrônicos e possíveis causas físicas."
        st.session_state.txt_analise = melhorar_texto_com_ia(rascunho_analise + ". " + prompt, "Análise Técnica")
        
    analise_final = st.text_area("Texto Final Análise:", value=st.session_state.txt_analise, height=150)

    # --- ETAPA 4: CONCLUSÃO ---
    st.write("### 4. Conclusão")
    if "txt_conclusao" not in st.session_state: st.session_state.txt_conclusao = ""
    
    rascunho_conclusao = st.text_area("Veredito:", placeholder="Ex: Não tem conserto. Foi raio. Garantia não cobre.", height=60)
    
    if st.button("Formalizar Conclusão", key="btn_conc"):
        prompt = "Escreva uma conclusão técnica formal, definindo o nexo causal e a recomendação final."
        st.session_state.txt_conclusao = melhorar_texto_com_ia(rascunho_conclusao + ". " + prompt, "Conclusão")
        
    conclusao_final = st.text_area("Texto Final Conclusão:", value=st.session_state.txt_conclusao, height=100)

    # --- BOTÃO FINAL ---
    if st.button("Gerar Parecer Técnico PDF", type="primary"):
        dados = {
            "cliente": cliente,
            "assunto": assunto,
            "responsavel": responsavel,
            "data": data,
            "historico": hist_final,
            "metodologia": metodologia,
            "analise": analise_final,
            "conclusao": conclusao_final
        }
        try:
            arquivo = gerar_pdf_parecer(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Parecer gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")
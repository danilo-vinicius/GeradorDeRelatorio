import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_visita(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE VISTORIA TÉCNICA")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Relatório de Visita Técnica",
        sub_titulo=f"Local: {dados['cliente']}\nAssunto: {dados['assunto']}",
        autor=dados['responsavel']
    )
    
    pdf.add_page()
    
    # Cabeçalho Interno
    pdf.set_y(30)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Visita: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. CENÁRIO ATUAL / DIAGNÓSTICO ---
    # Baseado no relatório SQS 206 e Goiânia (descrição detalhada dos problemas)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Diagnóstico e Cenário Encontrado", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['diagnostico'], align='J')
    pdf.ln(5)

    # --- 2. SERVIÇOS EXECUTADOS (Se houver) ---
    if len(dados['servicos']) > 5: # Só imprime se tiver texto
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. Intervenções Realizadas (Paliativas/Definitivas)", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['servicos'], align='J')
        pdf.ln(5)

    # --- 3. RECOMENDAÇÕES TÉCNICAS (O Ouro do relatório) ---
    # Baseado nas "Recomendações Urgentes" do relatório Goiânia
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. Recomendações e Proposta Técnica", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['recomendacoes'], align='J')
    pdf.ln(5)

    # --- 4. PENDÊNCIAS DO CLIENTE (Importante!) ---
    # Baseado no relatório QI 16 (Ações necessárias do cliente)
    if len(dados['pendencias']) > 5:
        pdf.set_fill_color(255, 240, 240) # Fundo levemente avermelhado para atenção
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "4. Adequações Necessárias (Responsabilidade do Cliente)", ln=True, fill=True)
        
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['pendencias'], align='J')
        pdf.ln(10)

    # --- 5. REGISTRO FOTOGRÁFICO ---
    # Baseado na estrutura visual do SQS 206 (Fotos grandes)
    if dados['fotos']:
        pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "5. Registro Fotográfico", ln=True)
        pdf.ln(5)
        
        # Loop para colocar fotos (2 por página para ficarem grandes e legíveis)
        for i, caminho_foto in enumerate(dados['fotos']):
            # Se for par e não for a primeira, verifica espaço
            if i > 0 and i % 2 == 0:
                pdf.add_page()
            
            if os.path.exists(caminho_foto):
                # Centraliza imagem
                pdf.image(caminho_foto, x=30, w=150)
                pdf.ln(2)
                # Legenda genérica (Poderíamos implementar legenda individual no futuro)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 5, f"Figura {i+1}: Registro das condições locais", align='C', ln=True)
                pdf.ln(10)

    # Assinatura
    pdf.bloco_assinatura(dados['responsavel'])
    
    nome_arquivo = f"Vistoria_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_visita():
    st.subheader("📋 Relatório de Vistoria Técnica Avançada")
    st.caption("Documentação completa de levantamento, diagnóstico e recomendações.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente / Local", value="Residencial SQS 206")
        assunto = st.text_input("Assunto Geral", value="Levantamento para Modernização de CFTV")
    with col2:
        responsavel = st.text_input("Responsável Técnico", value="Técnico Sênior")
        data = st.date_input("Data da Vistoria").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- 1. DIAGNÓSTICO (IA) ---
    st.write("### 1. Diagnóstico (O que você encontrou?)")
    if "txt_diag_visita" not in st.session_state: st.session_state.txt_diag_visita = ""
    
    rascunho_diag = st.text_area("Descreva os problemas:", 
                                placeholder="Ex: Fiação toda solta no pilotis, câmeras antigas que não pegam a noite, DVR apitando...",
                                height=80)
    
    if st.button("Formalizar Diagnóstico", key="btn_ia_diag", type="secondary"):
        prompt = "Descreva tecnicamente o cenário encontrado, enfatizando riscos, obsolescência e estado de conservação."
        st.session_state.txt_diag_visita = melhorar_texto_com_ia(rascunho_diag + ". " + prompt, "Diagnóstico de Vistoria")
        
    diag_final = st.text_area("Texto Final Diagnóstico:", value=st.session_state.txt_diag_visita, height=150)

    # --- 2. SERVIÇOS REALIZADOS (IA) ---
    st.write("### 2. O que foi feito na hora? (Opcional)")
    if "txt_serv_visita" not in st.session_state: st.session_state.txt_serv_visita = ""
    
    rascunho_serv = st.text_area("Houve intervenção imediata?", 
                                placeholder="Ex: Desliguei o buzzer do DVR e fixei o cabo solto com fita.", height=60)
    
    if st.button("Formalizar Serviços", key="btn_ia_serv", type="secondary"):
        prompt = "Descreva as ações paliativas ou definitivas realizadas durante a visita técnica."
        st.session_state.txt_serv_visita = melhorar_texto_com_ia(rascunho_serv + ". " + prompt, "Serviços em Vistoria")
        
    serv_final = st.text_area("Texto Final Serviços:", value=st.session_state.txt_serv_visita, height=100)

    # --- 3. RECOMENDAÇÕES (IA) ---
    st.write("### 3. Recomendações Técnicas (O que precisa ser feito?)")
    if "txt_rec_visita" not in st.session_state: st.session_state.txt_rec_visita = ""
    
    rascunho_rec = st.text_area("O que sugerimos?", 
                               placeholder="Ex: Trocar todas as câmeras por Full HD, passar tubulação nova galvanizada...",
                               height=80)
    
    if st.button("Formalizar Recomendações", key="btn_ia_rec", type="secondary"):
        prompt = "Liste recomendações técnicas em tópicos, focando em modernização, normas técnicas e segurança."
        st.session_state.txt_rec_visita = melhorar_texto_com_ia(rascunho_rec + ". " + prompt, "Recomendações Técnicas")
        
    rec_final = st.text_area("Texto Final Recomendações:", value=st.session_state.txt_rec_visita, height=150)

    # --- 4. PENDÊNCIAS CLIENTE ---
    st.write("### 4. Responsabilidades do Cliente (Infra/Civil)")
    st.caption("Ex: Pintura, poda de árvore, ponto de energia 110v.")
    pendencias = st.text_area("O que o cliente precisa providenciar?", height=80)

    # --- FOTOS ---
    st.markdown("---")
    st.write("### Registro Fotográfico")
    fotos = st.file_uploader("Selecione as fotos da vistoria", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

    if st.button("Gerar Relatório de Vistoria", type="primary"):
        lista_fotos = []
        if fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in fotos:
                caminho = f"temp/vistoria_{f.name}"
                with open(caminho, "wb") as file:
                    file.write(f.getbuffer())
                lista_fotos.append(caminho)

        dados = {
            "cliente": cliente,
            "assunto": assunto,
            "responsavel": responsavel,
            "data": data,
            "diagnostico": diag_final,
            "servicos": serv_final,
            "recomendacoes": rec_final,
            "pendencias": pendencias,
            "fotos": lista_fotos
        }

        try:
            arquivo = gerar_pdf_visita(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Relatório de Vistoria gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_relatorio_lpr(dados):
    # Título da Capa
    pdf = RelatorioBrasfort(titulo="Relatório de Ocorrência - Sistema LPR")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Relatório de Ocorrência - Sistema LPR",
        sub_titulo=f"Cliente: {dados['cliente']}\nUnidade: {dados['unidade']}",
        autor=dados['tecnico']
    )
    
    pdf.add_page()
    pdf.ln(5)

    # Título do Relatório
    pdf._set_font('B', 16)
    pdf.set_text_color(10, 35, 80)
    pdf.cell(0, 10, pdf.titulo_documento, 0, 1, 'C')
    pdf.ln(10)

    # Cabeçalho Interno
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Unidade: {dados['unidade']}", ln=True)
    pdf.cell(0, 6, f"Data: {dados['data']}", ln=True)
    pdf.ln(5)

    # --- 1. OBJETIVO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. OBJETIVO", ln=True)
    pdf.set_font('Barlow', '', 11)
    
    # Texto fiel aos exemplos [cite: 156]
    texto_obj = (f"Registrar e analisar, de forma técnica e objetiva, a ocorrência relatada pela unidade {dados['unidade']} "
                 "envolvendo o sistema de Leitura Automática de Placas (LPR), apontando evidências, "
                 "causas prováveis e providências adotadas.")
    pdf.multi_cell(0, 6, texto_obj, align='J')
    pdf.ln(5)

    # --- 2. METODOLOGIA (Fixo/Padrão) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. METODOLOGIA DE VERIFICAÇÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    # Itens extraídos dos relatórios [cite: 159-162]
    metodologia = (
        "- Consulta aos logs de eventos do LPR e da controladora de acesso.\n"
        "- Análise de gravações de vídeo das câmeras de Entrada/Saída.\n"
        "- Conferência dos cadastros de veículos vinculados à unidade.\n"
        "- Checagem do status do servidor LPR e conectividade."
    )
    pdf.multi_cell(0, 6, metodologia, align='J')
    pdf.ln(5)

    # --- 3. DESCRIÇÃO DA OCORRÊNCIA ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. DESCRIÇÃO DA OCORRÊNCIA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao'], align='J')
    pdf.ln(5)

    # --- 4. LINHA DO TEMPO E ANÁLISE ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. LINHA DO TEMPO E ANÁLISE TÉCNICA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['analise'], align='J')
    pdf.ln(5)

    # --- 5. CONCLUSÃO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "5. CONCLUSÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    # --- 6. ANEXOS (Fotos) ---
    if dados['lista_fotos']:
        # Se tiver pouco espaço, quebra página
        if pdf.get_y() > 200: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "6. ANEXOS (EVIDÊNCIAS)", ln=True)
        pdf.ln(5)
        
        for i, foto in enumerate(dados['lista_fotos']):
            if os.path.exists(foto):
                # Centraliza
                x_cent = (210 - 160) / 2
                
                # Verifica quebra de página para imagem
                if pdf.get_y() + 100 > 280: pdf.add_page()
                
                pdf.image(foto, x=x_cent, w=160)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"Evidência {i+1}: Registro visual / Log do sistema", align='C', ln=True)
                pdf.ln(5)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"LPR_{dados['unidade']}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_lpr():
    st.subheader("🚗 Relatório de Ocorrência - LPR")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Jardim das Cerejeiras")
        unidade = st.text_input("Unidade (Apt/Casa)", placeholder="Ex: Apt 411")
    with col2:
        tecnico = st.text_input("Técnico Responsável", value="Luciano Pereira do Nascimento")
        data = st.date_input("Data da Ocorrência").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- CAMPOS DE TEXTO ---
    
    # 1. DESCRIÇÃO
    st.write("### 📝 1. Descrição da Ocorrência")
    if "txt_lpr_desc" not in st.session_state: st.session_state.txt_lpr_desc = ""
    
    rascunho_desc = st.text_area("O que o morador relatou?", 
                                placeholder="Ex: Moradora do 411 disse que o portão não abriu na saída e usou o controle...", height=70)
    
    if st.button("Formalizar Descrição (IA)", key="btn_desc"):
        if len(rascunho_desc) > 5:
            with st.spinner("Reescrevendo..."):
                st.session_state.txt_lpr_desc = melhorar_texto_com_ia(rascunho_desc, "Relato de Ocorrência LPR")
    
    desc_final = st.text_area("Texto Final (Descrição):", value=st.session_state.txt_lpr_desc, height=100)

    # 2. ANÁLISE TÉCNICA
    st.write("### ⏱️ 2. Linha do Tempo e Análise")
    st.caption("Descreva o que foi visto nas câmeras e logs (horários e fatos).")
    if "txt_lpr_ana" not in st.session_state: st.session_state.txt_lpr_ana = ""
    
    rascunho_ana = st.text_area("Fatos apurados:", 
                               placeholder="Ex: 14:46:34 - Veículo parou muito na frente (além do balizador). 14:46:52 - Saiu sem leitura automática...", height=100)
    
    if st.button("Formalizar Análise (IA)", key="btn_ana"):
        if len(rascunho_ana) > 5:
            with st.spinner("Organizando cronologicamente..."):
                prompt = "Transforme em uma análise técnica cronológica de LPR: " + rascunho_ana
                st.session_state.txt_lpr_ana = melhorar_texto_com_ia(prompt, "Análise Técnica LPR")
                
    ana_final = st.text_area("Texto Final (Análise):", value=st.session_state.txt_lpr_ana, height=150)

    # 3. CONCLUSÃO
    st.write("### ✅ 3. Conclusão")
    opcoes_conclusao = [
        "Escrever manualmente...",
        "Sistema OK - Falha Operacional (Posicionamento incorreto)",
        "Sistema OK - Contingência (Uso de controle antes do tempo)",
        "Falha Técnica Confirmada (Instabilidade de Rede/Servidor)"
    ]
    escolha_conc = st.selectbox("Modelo de Conclusão:", options=opcoes_conclusao)
    
    texto_pre = ""
    if "Posicionamento" in escolha_conc:
        texto_pre = "O sistema operou normalmente. A ocorrência deveu-se ao posicionamento inadequado do veículo, fora da zona ideal de captura, impedindo a leitura automática."
    elif "Contingência" in escolha_conc:
        texto_pre = "O sistema estava processando a leitura dentro do tempo padrão (até 12s), porém o acionamento manual via controle remoto interrompeu o ciclo automático."
    elif "Falha Técnica" in escolha_conc:
        texto_pre = "Foi identificada instabilidade momentânea na comunicação entre o servidor LPR e a controladora, impedindo o envio do comando de abertura."

    conc_final = st.text_area("Texto Final (Conclusão):", value=texto_pre, height=100)

    # --- ANEXOS ---
    st.markdown("---")
    st.write("### 📷 Evidências")
    upload_fotos = st.file_uploader("Fotos e Logs", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

    if st.button("Gerar Relatório LPR", type="primary"):
        # Salva fotos
        lista_fotos = []
        if upload_fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for i, f in enumerate(upload_fotos):
                path = f"temp/lpr_{i}.jpg"
                with open(path, "wb") as file: file.write(f.getbuffer())
                lista_fotos.append(path)

        dados = {
            "cliente": cliente, "unidade": unidade, "tecnico": tecnico, "data": data,
            "descricao": desc_final, "analise": ana_final, "conclusao": conc_final,
            "lista_fotos": lista_fotos
        }

        try:
            arquivo = gerar_relatorio_lpr(dados)
            st.session_state['lpr_pronto'] = arquivo
            st.success("Relatório LPR Gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'lpr_pronto' in st.session_state:
        with open(st.session_state['lpr_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name=f"LPR_{dados['cliente'].replace(' ', '_')}_{dados['data'].replace('/','-')}.pdf")
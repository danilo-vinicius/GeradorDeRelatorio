import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

# --- MOTOR PDF (Mantido igual) ---
def gerar_relatorio_lpr(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    pdf.gerar_capa(titulo_principal="Relatório de Ocorrência - Sistema LPR", sub_titulo=f"Cliente: {dados['cliente']}\nUnidade: {dados['unidade']}\nData: {dados['data']}", autor=dados['tecnico'])
    pdf.add_page()
    pdf.ln(10)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Unidade: {dados['unidade']} - Data: {dados['data']}", ln=True)
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. OBJETIVO", ln=True)
    pdf.set_font('Barlow', '', 11)
    texto_obj = (f"Registrar e analisar, de forma técnica e objetiva, a ocorrência relatada pela unidade {dados['unidade']} "
                 "envolvendo o sistema de Leitura Automática de Placas (LPR), apontando evidências, causas prováveis e providências adotadas.")
    pdf.multi_cell(0, 6, texto_obj, align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. METODOLOGIA DE VERIFICAÇÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    metodologia = "- Consulta aos logs de eventos do LPR e controladora.\n- Análise de gravações de vídeo.\n- Conferência dos cadastros.\n- Checagem do status do servidor."
    pdf.multi_cell(0, 6, metodologia, align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. DESCRIÇÃO DA OCORRÊNCIA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. LINHA DO TEMPO E ANÁLISE TÉCNICA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['analise'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "5. CONCLUSÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "6. ANEXOS (EVIDÊNCIAS)", ln=True)
        pdf.ln(5)
        for i, foto in enumerate(dados['lista_fotos']):
            if os.path.exists(foto):
                if pdf.get_y() + 100 > 280: pdf.add_page()
                x_cent = (210 - 160) / 2
                pdf.image(foto, x=x_cent, w=160)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"Evidência {i+1}", align='C', ln=True)
                pdf.ln(5)

    pdf.bloco_assinatura(dados['tecnico'])
    nome_arquivo = f"LPR_{dados['unidade']}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE SPLIT ---
def renderizar_formulario_lpr():
    st.subheader("🚗 Relatório de Ocorrência - LPR")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO ===
    with col_form:
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio Jardim das Cerejeiras")
        unidade = c1.text_input("Unidade", placeholder="Ex: Apt 411")
        tecnico = c2.text_input("Técnico", value="Luciano Pereira")
        data = c2.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")
        st.write("### 1. Descrição")
        if "txt_lpr_desc" not in st.session_state: st.session_state.txt_lpr_desc = ""
        rascunho_desc = st.text_area("Relato do morador:", height=70, key="ras_desc")
        if st.button("IA: Formalizar", key="btn_desc"):
            st.session_state.txt_lpr_desc = melhorar_texto_com_ia(rascunho_desc, "Relato LPR")
            st.rerun()
        desc_final = st.text_area("Final:", value=st.session_state.txt_lpr_desc, height=100, key="fin_desc")

        st.write("### 2. Análise")
        if "txt_lpr_ana" not in st.session_state: st.session_state.txt_lpr_ana = ""
        rascunho_ana = st.text_area("O que viu nos logs?", height=100, key="ras_ana")
        if st.button("IA: Cronologia", key="btn_ana"):
            st.session_state.txt_lpr_ana = melhorar_texto_com_ia("Crie linha do tempo: " + rascunho_ana, "Análise LPR")
            st.rerun()
        ana_final = st.text_area("Final:", value=st.session_state.txt_lpr_ana, height=150, key="fin_ana")

        st.write("### 3. Conclusão")
        opcoes = ["Escrever...", "Sistema OK (Posicionamento)", "Sistema OK (Contingência)", "Falha Técnica"]
        escolha = st.selectbox("Modelo:", opcoes)
        
        texto_pre = ""
        if "Posicionamento" in escolha: texto_pre = "O sistema operou normalmente. A falha deveu-se ao posicionamento inadequado do veículo."
        elif "Contingência" in escolha: texto_pre = "O sistema estava processando, mas o usuário acionou o controle antes do tempo."
        elif "Falha" in escolha: texto_pre = "Identificada instabilidade na comunicação entre servidor e câmera."
        
        conc_final = st.text_area("Final:", value=texto_pre, height=100, key="fin_conc")

        st.markdown("---")
        upload_fotos = st.file_uploader("Evidências", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

    # === LADO DIREITO ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            lista_fotos = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for i, f in enumerate(upload_fotos):
                    path = f"temp/view_lpr_{i}.jpg"
                    with open(path, "wb") as file: file.write(f.getbuffer())
                    lista_fotos.append(path)

            dados = {
                "cliente": cliente, "unidade": unidade, "tecnico": tecnico, "data": data,
                "descricao": desc_final, "analise": ana_final, "conclusao": conc_final,
                "lista_fotos": lista_fotos
            }
            try:
                path = gerar_relatorio_lpr(dados)
                st.session_state['pdf_lpr_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_lpr_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_lpr_view'])
            with open(st.session_state['pdf_lpr_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "LPR.pdf", "application/pdf", use_container_width=True)
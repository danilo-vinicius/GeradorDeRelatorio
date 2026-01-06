import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

# --- MOTOR PDF (Mantido igual) ---
def gerar_pdf_vistoria(dados):
    titulo_capa = "RELATÓRIO DE VISTORIA TÉCNICA" if dados['tipo_relatorio'] == "Levantamento" else "RELATÓRIO DE VISITA TÉCNICA"
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    
    pdf.gerar_capa(titulo_principal=titulo_capa, sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}\nAssunto: {dados['assunto']}", autor=dados['tecnico'])
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Visita: {dados['data']}", ln=True)
    pdf.ln(10)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. OBJETIVO / INTRODUÇÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['introducao'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    titulo_secao2 = "2. CONSTATAÇÕES POR SETOR" if dados['tipo_relatorio'] == "Levantamento" else "2. DIAGNÓSTICO TÉCNICO E OCORRÊNCIAS"
    pdf.cell(0, 8, titulo_secao2, ln=True)
    pdf.ln(2)

    if dados['tipo_relatorio'] == "Levantamento" and dados['lista_constatacoes']:
        pdf.set_font('Barlow', 'B', 10)
        pdf.set_fill_color(10, 35, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(40, 8, "Setor / Local", 1, 0, 'C', True)
        pdf.cell(75, 8, "Situação Atual / Problema", 1, 0, 'C', True)
        pdf.cell(75, 8, "Recomendação Técnica", 1, 1, 'C', True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Barlow', '', 10)
        for item in dados['lista_constatacoes']:
            pdf.set_fill_color(245, 245, 245)
            y_inicio = pdf.get_y()
            pdf.set_xy(10, y_inicio)
            pdf.multi_cell(40, 6, item['local'], border='LTRB', align='L', fill=True)
            h1 = pdf.get_y() - y_inicio
            pdf.set_xy(50, y_inicio)
            pdf.multi_cell(75, 6, item['problema'], border='LTRB', align='L', fill=False)
            h2 = pdf.get_y() - y_inicio
            pdf.set_xy(125, y_inicio)
            pdf.multi_cell(75, 6, item['solucao'], border='LTRB', align='L', fill=False)
            h3 = pdf.get_y() - y_inicio
            altura_max = max(h1, h2, h3)
            pdf.set_y(y_inicio + altura_max)
        pdf.ln(5)
    else:
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['diagnostico_texto'], align='J')
        pdf.ln(5)

    if dados['recomendacoes']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. RECOMENDAÇÕES E LISTA DE MATERIAIS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['recomendacoes'], align='J')
        pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. CONCLUSÃO / PARECER FINAL", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    if dados['lista_fotos']:
        if pdf.get_y() > 220: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "ANEXO FOTOGRÁFICO", ln=True)
        pdf.ln(5)
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            legenda = item['legenda']
            if os.path.exists(caminho):
                if pdf.get_y() + 90 > 280: pdf.add_page()
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 10)
                pdf.cell(0, 6, f"Foto {i+1}: {legenda}", align='C', ln=True)
                pdf.ln(8)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Vistoria_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE SPLIT ---
def renderizar_formulario_visita():
    st.subheader("📋 Relatório de Visita Técnica / Vistoria")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO: FORMULÁRIO ===
    with col_form:
        tipo_relatorio = st.radio("Tipo de Relatório:", ["Diagnóstico (Texto Corrido)", "Levantamento (Tabela)"], horizontal=True)
        modo = "Diagnostico" if "Texto" in tipo_relatorio else "Levantamento"

        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio SQS 113")
        local = c1.text_input("Local / Referência", value="Bloco B")
        assunto = c1.text_input("Assunto Principal", value="Vistoria de Infraestrutura e CFTV")
        tecnico = c2.text_input("Técnico Responsável", value="Luciano Pereira")
        data = c2.date_input("Data da Visita").strftime("%d/%m/%Y")

        st.markdown("---")
        st.write("### 1. Introdução")
        if "txt_visita_intro" not in st.session_state: st.session_state.txt_visita_intro = ""
        rascunho_intro = st.text_area("Objetivo (Rascunho):", height=60, key="ras_intro")
        if st.button("IA: Formalizar Intro", key="btn_intro"):
            st.session_state.txt_visita_intro = melhorar_texto_com_ia(rascunho_intro, "Introdução")
            st.rerun()
        intro_final = st.text_area("Final:", value=st.session_state.txt_visita_intro, height=100, key="fin_intro")

        st.markdown("---")
        diagnostico_texto_final = ""
        lista_constatacoes = []

        if modo == "Diagnostico":
            st.write("### 2. Diagnóstico")
            if "txt_visita_diag" not in st.session_state: st.session_state.txt_visita_diag = ""
            rascunho_diag = st.text_area("O que foi encontrado?", height=150, key="ras_diag")
            if st.button("IA: Formalizar Diagnóstico", key="btn_diag"):
                st.session_state.txt_visita_diag = melhorar_texto_com_ia(rascunho_diag, "Diagnóstico")
                st.rerun()
            diagnostico_texto_final = st.text_area("Final:", value=st.session_state.txt_visita_diag, height=200, key="fin_diag")

        else: # LEVANTAMENTO
            st.write("### 2. Levantamento (Tabela)")
            if "tabela_vistoria" not in st.session_state: st.session_state.tabela_vistoria = []
            
            with st.container(border=True):
                c_tb1, c_tb2, c_tb3 = st.columns([1, 2, 2])
                t_local = c_tb1.text_input("Local", key="tb_loc")
                t_prob = c_tb2.text_area("Problema", height=60, key="tb_prob")
                t_sol = c_tb3.text_area("Solução", height=60, key="tb_sol")
                if st.button("➕ Adicionar Linha"):
                    st.session_state.tabela_vistoria.append({"local": t_local, "problema": t_prob, "solucao": t_sol})
                    st.rerun()
            
            if st.session_state.tabela_vistoria:
                st.table(st.session_state.tabela_vistoria)
                if st.button("Limpar Tabela"):
                    st.session_state.tabela_vistoria = []
                    st.rerun()
                lista_constatacoes = st.session_state.tabela_vistoria

        st.markdown("---")
        rec_final = st.text_area("3. Recomendações / Materiais:", height=100, key="rec_fin")

        st.write("### 4. Conclusão")
        if "txt_visita_conc" not in st.session_state: st.session_state.txt_visita_conc = ""
        rascunho_conc = st.text_area("Resumo final:", height=60, key="ras_conc")
        if st.button("IA: Concluir", key="btn_conc"):
            st.session_state.txt_visita_conc = melhorar_texto_com_ia(rascunho_conc, "Conclusão")
            st.rerun()
        conc_final = st.text_area("Final:", value=st.session_state.txt_visita_conc, height=100, key="fin_conc")

        st.markdown("---")
        upload_fotos = st.file_uploader("Fotos", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
        legendas = {}
        if upload_fotos:
            for f in upload_fotos:
                legendas[f.name] = st.text_input(f"Legenda {f.name}", value="Foto da vistoria", key=f"leg_{f.name}")

    # === LADO DIREITO: PREVIEW ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            lista_fotos_final = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for file in upload_fotos:
                    path = f"temp/view_vist_{file.name}"
                    with open(path, "wb") as f: f.write(file.getbuffer())
                    lista_fotos_final.append({"caminho": path, "legenda": legendas[file.name]})

            dados = {
                "tipo_relatorio": "Levantamento" if modo == "Levantamento" else "Diagnostico",
                "cliente": cliente, "local": local, "assunto": assunto, "tecnico": tecnico, "data": data,
                "introducao": intro_final,
                "diagnostico_texto": diagnostico_texto_final,
                "lista_constatacoes": lista_constatacoes,
                "recomendacoes": rec_final,
                "conclusao": conc_final,
                "lista_fotos": lista_fotos_final
            }
            try:
                path = gerar_pdf_vistoria(dados)
                st.session_state['pdf_vistoria_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_vistoria_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_vistoria_view'])
            with open(st.session_state['pdf_vistoria_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Vistoria.pdf", "application/pdf", use_container_width=True)
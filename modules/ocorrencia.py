import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

def gerar_pdf_ocorrencia(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    pdf.gerar_capa(titulo_principal="Relatório de Ocorrência Técnica", sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}\nData: {dados['data']}", autor=dados['tecnico'])
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Local: {dados['local']} - Data: {dados['data']}", ln=True)
    pdf.ln(10)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. DESCRIÇÃO DA OCORRÊNCIA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. IMPACTO OPERACIONAL", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['impacto'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. AÇÕES TÉCNICAS EXECUTADAS", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['acoes'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. ESTADO ATUAL E RECOMENDAÇÕES", ln=True)
    pdf.set_font('Barlow', '', 11)
    texto_final = f"Situação Atual: {dados['status']}\n\nRecomendação: {dados['recomendacao']}"
    pdf.multi_cell(0, 6, texto_final, align='J')
    pdf.ln(10)

    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "5. REGISTRO FOTOGRÁFICO", ln=True)
        pdf.ln(5)
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            legenda = item['legenda']
            if os.path.exists(caminho):
                if pdf.get_y() + 90 > 280: pdf.add_page()
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"{legenda}", align='C', ln=True)
                pdf.ln(8)

    pdf.bloco_assinatura(dados['tecnico'])
    nome_arquivo = f"Ocorrencia_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

def renderizar_formulario_ocorrencia():
    st.subheader("⚠️ Relatório de Ocorrência")
    col_form, col_view = st.columns([0.55, 0.45])

    with col_form:
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Usina São Pedro")
        local = c1.text_input("Local", value="Perímetro")
        tecnico = c2.text_input("Técnico", value="Luciano Pereira")
        data = c2.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")
        st.write("### 1. O que aconteceu?")
        if "txt_oco_desc" not in st.session_state: st.session_state.txt_oco_desc = ""
        rascunho_desc = st.text_area("Relato (Rascunho):", height=70, key="ras_desc")
        if st.button("IA: Formalizar Relato", key="btn_desc"):
            st.session_state.txt_oco_desc = melhorar_texto_com_ia(rascunho_desc, "Relato Incidente")
            st.rerun()
        desc_final = st.text_area("Final:", value=st.session_state.txt_oco_desc, height=100, key="fin_desc")

        st.write("### 2. Impacto")
        if "txt_oco_imp" not in st.session_state: st.session_state.txt_oco_imp = ""
        rascunho_imp = st.text_area("O que parou?", height=60, key="ras_imp")
        if st.button("IA: Formalizar Impacto", key="btn_imp"):
            st.session_state.txt_oco_imp = melhorar_texto_com_ia(rascunho_imp, "Impacto")
            st.rerun()
        imp_final = st.text_area("Final:", value=st.session_state.txt_oco_imp, height=80, key="fin_imp")

        st.write("### 3. Ações")
        if "txt_oco_acao" not in st.session_state: st.session_state.txt_oco_acao = ""
        rascunho_acao = st.text_area("O que foi feito?", height=60, key="ras_acao")
        if st.button("IA: Formalizar Ações", key="btn_acao"):
            st.session_state.txt_oco_acao = melhorar_texto_com_ia(rascunho_acao, "Ações Corretivas")
            st.rerun()
        acao_final = st.text_area("Final:", value=st.session_state.txt_oco_acao, height=80, key="fin_acao")

        c1, c2 = st.columns(2)
        status_atual = c1.selectbox("Status:", ["Operacional", "Parcial", "Inoperante"])
        recomendacao = c2.text_input("Recomendação:", placeholder="Ex: Troca de cabo")

        st.markdown("---")
        upload_fotos = st.file_uploader("Fotos", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
        legendas = {}
        if upload_fotos:
            for f in upload_fotos:
                legendas[f.name] = st.text_input(f"Legenda {f.name}", value="Avaria", key=f"leg_{f.name}")

    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            lista_fotos = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for f in upload_fotos:
                    path = f"temp/view_oco_{f.name}"
                    with open(path, "wb") as file: file.write(f.getbuffer())
                    lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

            dados = {
                "cliente": cliente, "local": local, "tecnico": tecnico, "data": data,
                "descricao": desc_final, "impacto": imp_final, "acoes": acao_final,
                "status": status_atual, "recomendacao": recomendacao,
                "lista_fotos": lista_fotos
            }
            try:
                path = gerar_pdf_ocorrencia(dados)
                st.session_state['pdf_oco_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_oco_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_oco_view'])
            with open(st.session_state['pdf_oco_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Ocorrencia.pdf", "application/pdf", use_container_width=True)
import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

def gerar_pdf_geral(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    pdf.gerar_capa(titulo_principal=dados['titulo_capa'], sub_titulo=f"Cliente: {dados['cliente']}\nAssunto: {dados['assunto']}", autor=dados['tecnico'])
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data: {dados['data']} - Assunto: {dados['assunto']}", ln=True)
    pdf.ln(10)

    secoes = [
        (dados['t1'], dados['c1']), (dados['t2'], dados['c2']),
        (dados['t3'], dados['c3']), (dados['t4'], dados['c4']),
    ]

    for titulo, conteudo in secoes:
        if conteudo and len(conteudo.strip()) > 0:
            pdf.set_font('Barlow', 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, titulo.upper(), ln=True)
            pdf.set_font('Barlow', '', 11)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, conteudo, align='J')
            pdf.ln(5)

    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "ANEXOS / EVIDÊNCIAS", ln=True)
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
    
    nome_arquivo = f"Relatorio_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

def renderizar_relatorio_geral():
    st.subheader("📝 Relatório Geral (Flexível)")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO ===
    with col_form:
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio...")
        titulo_capa = c1.text_input("Título Capa", value="RELATÓRIO TÉCNICO")
        tecnico = c2.text_input("Técnico", value="Seu Nome")
        assunto = c2.text_input("Assunto", value="Esclarecimento")
        data = c2.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")
        t1 = st.text_input("Título 1:", value="1. INTRODUÇÃO")
        if "txt_geral_1" not in st.session_state: st.session_state.txt_geral_1 = ""
        c1_txt = st.text_area("Texto 1:", height=100, key="area_1", value=st.session_state.txt_geral_1)
        if st.button("IA: Melhorar 1", key="ia_1"):
            st.session_state.txt_geral_1 = melhorar_texto_com_ia(c1_txt, "Introdução")
            st.rerun()

        st.markdown("---")
        t2 = st.text_input("Título 2:", value="2. DESENVOLVIMENTO")
        if "txt_geral_2" not in st.session_state: st.session_state.txt_geral_2 = ""
        c2_txt = st.text_area("Texto 2:", height=150, key="area_2", value=st.session_state.txt_geral_2)
        if st.button("IA: Melhorar 2", key="ia_2"):
            st.session_state.txt_geral_2 = melhorar_texto_com_ia(c2_txt, "Técnico")
            st.rerun()

        st.markdown("---")
        t3 = st.text_input("Título 3:", value="3. OBSERVAÇÕES")
        if "txt_geral_3" not in st.session_state: st.session_state.txt_geral_3 = ""
        c3_txt = st.text_area("Texto 3:", height=100, key="area_3", value=st.session_state.txt_geral_3)
        if st.button("IA: Melhorar 3", key="ia_3"):
            st.session_state.txt_geral_3 = melhorar_texto_com_ia(c3_txt, "Obs")
            st.rerun()

        st.markdown("---")
        t4 = st.text_input("Título 4:", value="4. CONCLUSÃO")
        if "txt_geral_4" not in st.session_state: st.session_state.txt_geral_4 = ""
        c4_txt = st.text_area("Texto 4:", height=100, key="area_4", value=st.session_state.txt_geral_4)
        if st.button("IA: Melhorar 4", key="ia_4"):
            st.session_state.txt_geral_4 = melhorar_texto_com_ia(c4_txt, "Conclusão")
            st.rerun()

        st.markdown("---")
        upload_fotos = st.file_uploader("Anexos", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
        legendas = {}
        if upload_fotos:
            for f in upload_fotos:
                legendas[f.name] = st.text_input(f"Legenda {f.name}", value="Anexo", key=f"leg_{f.name}")

    # === LADO DIREITO ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            lista_fotos = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for f in upload_fotos:
                    path = f"temp/view_geral_{f.name}"
                    with open(path, "wb") as file: file.write(f.getbuffer())
                    lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

            dados = {
                "cliente": cliente, "tecnico": tecnico, "assunto": assunto, "data": data, "titulo_capa": titulo_capa,
                "t1": t1, "c1": st.session_state.txt_geral_1 if st.session_state.txt_geral_1 else c1_txt,
                "t2": t2, "c2": st.session_state.txt_geral_2 if st.session_state.txt_geral_2 else c2_txt,
                "t3": t3, "c3": st.session_state.txt_geral_3 if st.session_state.txt_geral_3 else c3_txt,
                "t4": t4, "c4": st.session_state.txt_geral_4 if st.session_state.txt_geral_4 else c4_txt,
                "lista_fotos": lista_fotos
            }
            try:
                path = gerar_pdf_geral(dados)
                st.session_state['pdf_geral_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_geral_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_geral_view'])
            with open(st.session_state['pdf_geral_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Relatorio_Geral.pdf", "application/pdf", use_container_width=True)
import streamlit as st
import os
import pandas as pd
from utils.brasfort_pdf import RelatorioBrasfort
from utils.visualizador import exibir_pdf_na_tela

# --- MOTOR PDF (MANTIDO IGUAL) ---
def gerar_pdf_universal(metadados, elementos):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO CORPORATIVO")
    
    pdf.gerar_capa(
        titulo_principal=metadados['titulo'],
        sub_titulo=f"{metadados['subtitulo']}\n\nDepartamento: {metadados['departamento']}",
        autor=metadados['autor']
    )
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, metadados['titulo'], ln=True)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, f"Data: {metadados['data']} | Autor: {metadados['autor']}", ln=True)
    pdf.ln(10)

    for item in elementos:
        if item['tipo'] == 'texto':
            if item['titulo']:
                pdf.set_font('Barlow', 'B', 12)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 8, item['titulo'].upper(), ln=True)
            if item['conteudo']:
                pdf.set_font('Barlow', '', 11)
                pdf.set_text_color(0, 0, 0)
                pdf.multi_cell(0, 6, item['conteudo'], align='J')
            pdf.ln(5)

        elif item['tipo'] == 'tabela':
            if item['titulo']:
                pdf.set_font('Barlow', 'B', 12)
                pdf.cell(0, 8, item['titulo'], ln=True)
                pdf.ln(2)
            if not item['conteudo'].empty:
                pdf.set_font('Barlow', 'B', 10)
                pdf.set_fill_color(10, 35, 80)
                pdf.set_text_color(255, 255, 255)
                colunas = item['conteudo'].columns
                largura_col = 190 / len(colunas)
                for col in colunas:
                    pdf.cell(largura_col, 8, str(col), 1, 0, 'C', True)
                pdf.ln()
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Barlow', '', 10)
                for index, row in item['conteudo'].iterrows():
                    fill = True if index % 2 == 0 else False
                    pdf.set_fill_color(240, 240, 240)
                    for col in colunas:
                        texto_celula = str(row[col])
                        pdf.cell(largura_col, 8, texto_celula, 1, 0, 'C', fill)
                    pdf.ln()
            pdf.ln(5)

        elif item['tipo'] == 'imagem':
            if item['titulo']:
                pdf.set_font('Barlow', 'B', 12)
                pdf.cell(0, 8, item['titulo'], ln=True)
            if item['arquivo'] and os.path.exists(item['arquivo']):
                if pdf.get_y() + 100 > 280: pdf.add_page()
                x_pos = (210 - 140) / 2
                pdf.image(item['arquivo'], x=x_pos, w=140)
                pdf.ln(2)
                if item['legenda']:
                    pdf.set_font('Barlow', 'I', 9)
                    pdf.cell(0, 6, item['legenda'], 0, 1, 'C')
            pdf.ln(5)

        elif item['tipo'] == 'assinatura':
            pdf.ln(15)
            if pdf.get_y() > 250: pdf.add_page()
            pdf.set_draw_color(0, 0, 0)
            pdf.line(20, pdf.get_y(), 100, pdf.get_y())
            pdf.ln(2)
            pdf.set_font('Barlow', 'B', 10)
            pdf.cell(0, 5, item['nome'], ln=True)
            pdf.set_font('Barlow', '', 9)
            pdf.cell(0, 5, item['cargo'], ln=True)
            pdf.ln(10)

    nome_safe = metadados['titulo'].replace(" ", "_")[:15]
    nome_arquivo = f"Doc_{nome_safe}_{metadados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE SPLIT ---
def renderizar_universal():
    st.subheader("🏢 Gerador Universal")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO ===
    with col_form:
        with st.expander("1. Configuração da Capa", expanded=True):
            c1, c2 = st.columns(2)
            titulo = c1.text_input("Título", value="RELATÓRIO DE GESTÃO")
            departamento = c1.selectbox("Depto", ["Segurança", "RH", "Financeiro", "Operacional", "TI"])
            subtitulo = c2.text_input("Subtítulo", value="Mês de Janeiro")
            autor = c2.text_input("Autor", value="Seu Nome")
            data = c2.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")
        st.write("### 2. Blocos de Conteúdo")
        
        if 'blocos_universal' not in st.session_state: st.session_state.blocos_universal = []

        # Barra de Botões
        cb1, cb2, cb3, cb4, cb5 = st.columns(5)
        if cb1.button("➕ Texto"): st.session_state.blocos_universal.append({"tipo": "texto", "titulo": "", "conteudo": ""})
        if cb2.button("➕ Tabela"): 
            st.session_state.blocos_universal.append({"tipo": "tabela", "titulo": "", "conteudo": pd.DataFrame({"Item": ["A"], "Qtd": [1]})})
        if cb3.button("➕ Foto"): st.session_state.blocos_universal.append({"tipo": "imagem", "titulo": "", "arquivo": None, "legenda": ""})
        if cb4.button("➕ Assin."): st.session_state.blocos_universal.append({"tipo": "assinatura", "nome": autor, "cargo": departamento})
        if cb5.button("Limpar"): 
            st.session_state.blocos_universal = []
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Renderização dos Blocos
        for i, bloco in enumerate(st.session_state.blocos_universal):
            with st.container(border=True):
                ch1, ch2 = st.columns([0.9, 0.1])
                ch1.caption(f"Bloco {i+1}: {bloco['tipo'].upper()}")
                if ch2.button("X", key=f"del_{i}"):
                    st.session_state.blocos_universal.pop(i)
                    st.rerun()

                if bloco['tipo'] == "texto":
                    bloco['titulo'] = st.text_input(f"Título ##{i}", value=bloco['titulo'], key=f"t_tit_{i}")
                    bloco['conteudo'] = st.text_area(f"Conteúdo ##{i}", value=bloco['conteudo'], height=100, key=f"t_cont_{i}")

                elif bloco['tipo'] == "tabela":
                    bloco['titulo'] = st.text_input(f"Título Tabela ##{i}", value=bloco['titulo'], key=f"tb_tit_{i}")
                    bloco['conteudo'] = st.data_editor(bloco['conteudo'], num_rows="dynamic", key=f"tb_edit_{i}")

                elif bloco['tipo'] == "imagem":
                    bloco['titulo'] = st.text_input(f"Título Imagem ##{i}", value=bloco['titulo'], key=f"img_tit_{i}")
                    uploaded = st.file_uploader(f"Arquivo ##{i}", type=['jpg', 'png'], key=f"up_{i}")
                    if uploaded:
                        if not os.path.exists("temp"): os.makedirs("temp")
                        path = f"temp/univ_{i}_{uploaded.name}"
                        with open(path, "wb") as f: f.write(uploaded.getbuffer())
                        bloco['arquivo'] = path
                        st.image(uploaded, width=150)
                    bloco['legenda'] = st.text_input(f"Legenda ##{i}", value=bloco['legenda'], key=f"leg_{i}")

                elif bloco['tipo'] == "assinatura":
                    ca1, ca2 = st.columns(2)
                    bloco['nome'] = ca1.text_input(f"Nome ##{i}", value=bloco['nome'], key=f"ass_n_{i}")
                    bloco['cargo'] = ca2.text_input(f"Cargo ##{i}", value=bloco['cargo'], key=f"ass_c_{i}")

    # === LADO DIREITO ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            if not st.session_state.blocos_universal:
                st.error("Adicione blocos.")
            else:
                metadados = {"titulo": titulo, "subtitulo": subtitulo, "departamento": departamento, "autor": autor, "data": data}
                try:
                    path = gerar_pdf_universal(metadados, st.session_state.blocos_universal)
                    st.session_state['pdf_univ_view'] = path
                    st.toast("Atualizado!", icon="✅")
                except Exception as e:
                    st.error(f"Erro: {e}")

        if 'pdf_univ_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_univ_view'])
            with open(st.session_state['pdf_univ_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Documento.pdf", "application/pdf", use_container_width=True)
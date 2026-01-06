import streamlit as st
import os
import pandas as pd
from utils.brasfort_pdf import RelatorioBrasfort

# --- MOTOR PDF DINÂMICO ---
def gerar_pdf_universal(metadados, elementos):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO CORPORATIVO")
    
    # 1. Capa Personalizada
    pdf.gerar_capa(
        titulo_principal=metadados['titulo'],
        sub_titulo=f"{metadados['subtitulo']}\n\nDepartamento: {metadados['departamento']}",
        autor=metadados['autor']
    )
    
    pdf.add_page()
    pdf.ln(20)

    # Cabeçalho Interno
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, metadados['titulo'], ln=True)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, f"Data: {metadados['data']} | Autor: {metadados['autor']}", ln=True)
    pdf.ln(10)

    # --- 2. RENDERIZAÇÃO DOS BLOCOS (O LEGO) ---
    for item in elementos:
        
        # --- BLOCO DE TEXTO ---
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

        # --- BLOCO DE TABELA ---
        elif item['tipo'] == 'tabela':
            if item['titulo']:
                pdf.set_font('Barlow', 'B', 12)
                pdf.cell(0, 8, item['titulo'], ln=True)
                pdf.ln(2)
            
            # Renderiza Tabela
            if not item['conteudo'].empty:
                # Configurações da Tabela
                pdf.set_font('Barlow', 'B', 10)
                pdf.set_fill_color(10, 35, 80) # Azul Brasfort
                pdf.set_text_color(255, 255, 255)
                
                # Largura dinâmica das colunas (divide 190mm pelo num de colunas)
                colunas = item['conteudo'].columns
                largura_col = 190 / len(colunas)
                
                # Cabeçalho
                for col in colunas:
                    pdf.cell(largura_col, 8, str(col), 1, 0, 'C', True)
                pdf.ln()
                
                # Linhas
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Barlow', '', 10)
                
                for index, row in item['conteudo'].iterrows():
                    # Alterna cor (Zebrado)
                    fill = True if index % 2 == 0 else False
                    pdf.set_fill_color(240, 240, 240)
                    
                    for col in colunas:
                        texto_celula = str(row[col])
                        pdf.cell(largura_col, 8, texto_celula, 1, 0, 'C', fill)
                    pdf.ln()
            pdf.ln(5)

        # --- BLOCO DE IMAGEM ---
        elif item['tipo'] == 'imagem':
            if item['titulo']:
                pdf.set_font('Barlow', 'B', 12)
                pdf.cell(0, 8, item['titulo'], ln=True)
            
            if item['arquivo'] and os.path.exists(item['arquivo']):
                # Verifica espaço
                if pdf.get_y() + 100 > 280: pdf.add_page()
                
                # Centraliza
                x_pos = (210 - 140) / 2
                pdf.image(item['arquivo'], x=x_pos, w=140)
                pdf.ln(2)
                
                if item['legenda']:
                    pdf.set_font('Barlow', 'I', 9)
                    pdf.cell(0, 6, item['legenda'], 0, 1, 'C')
            pdf.ln(5)

        # --- BLOCO DE ASSINATURA ---
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

    # Salva
    nome_safe = metadados['titulo'].replace(" ", "_")[:15]
    nome_arquivo = f"Doc_{nome_safe}_{metadados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_universal():
    st.subheader("🏢 Gerador de Documentos Universal")
    st.caption("Ferramenta padrão Brasfort para criação de relatórios, ofícios e comunicados.")

    # --- 1. CONFIGURAÇÃO DA CAPA ---
    with st.expander("1. Configuração do Documento (Capa)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            titulo = st.text_input("Título Principal", value="RELATÓRIO DE GESTÃO")
            departamento = st.selectbox("Departamento", ["Segurança Eletrônica", "RH / DP", "Financeiro", "Operacional", "TI", "Administrativo"])
        with c2:
            subtitulo = st.text_input("Subtítulo / Cliente", value="Referente ao mês de Janeiro")
            autor = st.text_input("Autor do Documento", value="Seu Nome")
        
        data = st.date_input("Data do Documento").strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("### 2. Construção do Conteúdo")
    
    # INICIALIZA O ESTADO (LISTA DE BLOCOS)
    if 'blocos_universal' not in st.session_state:
        st.session_state.blocos_universal = []

    # --- BARRA DE FERRAMENTAS (BOTOES DE ADICIONAR) ---
    col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)
    
    with col_btn1:
        if st.button("➕ Texto"):
            st.session_state.blocos_universal.append({"tipo": "texto", "titulo": "", "conteudo": ""})
    with col_btn2:
        if st.button("➕ Tabela"):
            # Cria um dataframe vazio inicial
            df_init = pd.DataFrame({"Item": ["Exemplo"], "Qtd": ["1"], "Status": ["OK"]})
            st.session_state.blocos_universal.append({"tipo": "tabela", "titulo": "", "conteudo": df_init})
    with col_btn3:
        if st.button("➕ Imagem"):
            st.session_state.blocos_universal.append({"tipo": "imagem", "titulo": "", "arquivo": None, "legenda": ""})
    with col_btn4:
        if st.button("➕ Assinatura"):
            st.session_state.blocos_universal.append({"tipo": "assinatura", "nome": autor, "cargo": departamento})
    with col_btn5:
        if st.button("🗑️ Limpar Tudo", type="primary"):
            st.session_state.blocos_universal = []
            st.rerun()

    # --- RENDERIZAÇÃO DOS BLOCOS NA TELA (PARA EDIÇÃO) ---
    st.markdown("<br>", unsafe_allow_html=True)
    
    for i, bloco in enumerate(st.session_state.blocos_universal):
        with st.container(border=True):
            cols = st.columns([0.9, 0.1])
            with cols[0]:
                st.caption(f"Bloco {i+1}: {bloco['tipo'].upper()}")
            with cols[1]:
                # Botão para remover este bloco específico
                if st.button("X", key=f"del_{i}"):
                    st.session_state.blocos_universal.pop(i)
                    st.rerun()

            # --- EDITOR DE TEXTO ---
            if bloco['tipo'] == "texto":
                bloco['titulo'] = st.text_input(f"Título da Seção (Opcional) ##{i}", value=bloco['titulo'], key=f"t_tit_{i}")
                bloco['conteudo'] = st.text_area(f"Conteúdo do Texto ##{i}", value=bloco['conteudo'], height=150, key=f"t_cont_{i}")

            # --- EDITOR DE TABELA ---
            elif bloco['tipo'] == "tabela":
                bloco['titulo'] = st.text_input(f"Título da Tabela ##{i}", value=bloco['titulo'], key=f"tb_tit_{i}")
                st.info("Edite a tabela abaixo. Adicione linhas clicando no '+' da tabela.")
                # Data Editor permite editar a tabela direto na tela!
                bloco['conteudo'] = st.data_editor(bloco['conteudo'], num_rows="dynamic", key=f"tb_edit_{i}")

            # --- EDITOR DE IMAGEM ---
            elif bloco['tipo'] == "imagem":
                bloco['titulo'] = st.text_input(f"Título da Imagem (Opcional) ##{i}", value=bloco['titulo'], key=f"img_tit_{i}")
                
                uploaded = st.file_uploader(f"Escolher Imagem ##{i}", type=['jpg', 'png', 'jpeg'], key=f"up_{i}")
                if uploaded:
                    if not os.path.exists("temp"): os.makedirs("temp")
                    path = f"temp/univ_{i}_{uploaded.name}"
                    with open(path, "wb") as f: f.write(uploaded.getbuffer())
                    bloco['arquivo'] = path
                    st.image(uploaded, width=200)
                
                bloco['legenda'] = st.text_input(f"Legenda da Foto ##{i}", value=bloco['legenda'], key=f"leg_{i}")

            # --- EDITOR DE ASSINATURA ---
            elif bloco['tipo'] == "assinatura":
                c_ass1, c_ass2 = st.columns(2)
                bloco['nome'] = c_ass1.text_input(f"Nome do Signatário ##{i}", value=bloco['nome'], key=f"ass_n_{i}")
                bloco['cargo'] = c_ass2.text_input(f"Cargo / Depto ##{i}", value=bloco['cargo'], key=f"ass_c_{i}")

    # --- BOTÃO FINAL ---
    st.markdown("---")
    if st.button("🖨️ Gerar Documento PDF", type="primary", use_container_width=True):
        if not st.session_state.blocos_universal:
            st.error("Adicione pelo menos um bloco de conteúdo.")
        else:
            metadados = {
                "titulo": titulo, "subtitulo": subtitulo, "departamento": departamento,
                "autor": autor, "data": data
            }
            try:
                arquivo = gerar_pdf_universal(metadados, st.session_state.blocos_universal)
                st.session_state['universal_pronto'] = arquivo
                st.success("Documento gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar: {e}")

    if 'universal_pronto' in st.session_state:
        with open(st.session_state['universal_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name="Documento_Brasfort.pdf", mime="application/pdf")
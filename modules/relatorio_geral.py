import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_geral(dados):
    #pdf = RelatorioBrasfort(titulo=f"{titulo_capa}")
    pdf = RelatorioBrasfort(titulo=dados['titulo_capa'])
    
    # Capa Genérica
    pdf.gerar_capa(
        titulo_principal=dados['titulo_capa'], # Título personalizável da capa
        sub_titulo=f"Cliente: {dados['cliente']}\nAssunto: {dados['assunto']}",
        autor=dados['tecnico']
    )

    pdf.add_page()
    pdf.ln(5)

    # Título do Relatório
    pdf._set_font('B', 16)
    pdf.set_text_color(10, 35, 80)
    pdf.cell(0, 10, pdf.titulo_documento, 0, 1, 'C')
    pdf.ln(5)

    # Cabeçalho Interno
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data: {dados['data']} - Assunto: {dados['assunto']}", ln=True)
    pdf.ln(10)

    # --- LOOP DE SEÇÕES DINÂMICAS ---
    # Aqui está a mágica: Ele só imprime se tiver texto!
    
    secoes = [
        (dados['t1'], dados['c1']), # Título 1, Conteúdo 1
        (dados['t2'], dados['c2']),
        (dados['t3'], dados['c3']),
        (dados['t4'], dados['c4']),
    ]

    for titulo, conteudo in secoes:
        # Se o conteúdo não for vazio (strip remove espaços em branco)
        if conteudo and len(conteudo.strip()) > 0:
            pdf.set_font('Barlow', 'B', 12)
            pdf.set_text_color(10, 35, 80) # <--- força os titulos para ficarem azuis
            # Imprime o título em Maiúsculas
            pdf.cell(0, 8, titulo.upper(), ln=True)
            
            pdf.set_font('Barlow', '', 11)
            pdf.set_text_color(0, 0, 0) # <--- força a cor do corpo do texto - preto
            pdf.multi_cell(0, 6, conteudo, align='J')
            pdf.ln(5) # Espaço entre seções

    # --- FOTOS ---
    if dados['lista_fotos']:
        # Verifica se precisa de nova página
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
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_relatorio_geral():
    st.subheader("📝 Relatório Geral (Flexível)")
    st.caption("Crie relatórios livres. Seções vazias não aparecerão no PDF.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio...")
        titulo_capa = st.text_input("Título da Capa", value="RELATÓRIO TÉCNICO")
    with col2:
        tecnico = st.text_input("Técnico", value="Seu Nome")
        assunto = st.text_input("Assunto", value="Esclarecimento Técnico")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- SEÇÃO 1 ---
    c1, c2 = st.columns([3, 1])
    with c1: 
        t1 = st.text_input("Título Seção 1:", value="1. INTRODUÇÃO / CONTEXTO")
    
    if "txt_geral_1" not in st.session_state: st.session_state.txt_geral_1 = ""
    c1_txt = st.text_area("Texto Seção 1:", height=100, key="area_1", value=st.session_state.txt_geral_1)
    
    if st.button("✨ Melhorar Texto 1", key="ia_1"):
        st.session_state.txt_geral_1 = melhorar_texto_com_ia(c1_txt, "Introdução Formal")
        st.rerun()

    # --- SEÇÃO 2 ---
    st.markdown("---")
    c1, c2 = st.columns([3, 1])
    with c1: 
        t2 = st.text_input("Título Seção 2:", value="2. DESENVOLVIMENTO / RESPOSTA")
    
    if "txt_geral_2" not in st.session_state: st.session_state.txt_geral_2 = ""
    c2_txt = st.text_area("Texto Seção 2 (Deixe vazio para ocultar):", height=150, key="area_2", value=st.session_state.txt_geral_2)
    
    if st.button("✨ Melhorar Texto 2", key="ia_2"):
        st.session_state.txt_geral_2 = melhorar_texto_com_ia(c2_txt, "Explicação Técnica")
        st.rerun()

    # --- SEÇÃO 3 ---
    st.markdown("---")
    c1, c2 = st.columns([3, 1])
    with c1: 
        t3 = st.text_input("Título Seção 3:", value="3. OBSERVAÇÕES ADICIONAIS")
    
    if "txt_geral_3" not in st.session_state: st.session_state.txt_geral_3 = ""
    c3_txt = st.text_area("Texto Seção 3 (Deixe vazio para ocultar):", height=100, key="area_3", value=st.session_state.txt_geral_3)
    
    if st.button("✨ Melhorar Texto 3", key="ia_3"):
        st.session_state.txt_geral_3 = melhorar_texto_com_ia(c3_txt, "Observações")
        st.rerun()

    # --- SEÇÃO 4 (CONCLUSÃO) ---
    st.markdown("---")
    c1, c2 = st.columns([3, 1])
    with c1: 
        t4 = st.text_input("Título Seção 4:", value="4. CONCLUSÃO")
    
    if "txt_geral_4" not in st.session_state: st.session_state.txt_geral_4 = ""
    c4_txt = st.text_area("Texto Seção 4 (Deixe vazio para ocultar):", height=100, key="area_4", value=st.session_state.txt_geral_4)
    
    if st.button("✨ Melhorar Texto 4", key="ia_4"):
        st.session_state.txt_geral_4 = melhorar_texto_com_ia(c4_txt, "Conclusão")
        st.rerun()

    # --- FOTOS ---
    st.markdown("---")
    upload_fotos = st.file_uploader("Anexos (Opcional)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    legendas = {}
    if upload_fotos:
        for f in upload_fotos:
            legendas[f.name] = st.text_input(f"Legenda para {f.name}", value="Anexo", key=f"leg_{f.name}")

    # --- GERAR ---
    if st.button("Gerar Relatório Geral", type="primary"):
        lista_fotos = []
        if upload_fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in upload_fotos:
                path = f"temp/geral_{f.name}"
                with open(path, "wb") as file: file.write(f.getbuffer())
                lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

        # Note que passamos session_state para garantir que o texto atualizado pela IA vá para o PDF
        dados = {
            "cliente": cliente, "tecnico": tecnico, "assunto": assunto, "data": data,
            "titulo_capa": titulo_capa,
            "t1": t1, "c1": st.session_state.txt_geral_1 if st.session_state.txt_geral_1 else c1_txt,
            "t2": t2, "c2": st.session_state.txt_geral_2 if st.session_state.txt_geral_2 else c2_txt,
            "t3": t3, "c3": st.session_state.txt_geral_3 if st.session_state.txt_geral_3 else c3_txt,
            "t4": t4, "c4": st.session_state.txt_geral_4 if st.session_state.txt_geral_4 else c4_txt,
            "lista_fotos": lista_fotos
        }

        try:
            arquivo = gerar_pdf_geral(dados)
            st.session_state['geral_pronto'] = arquivo
            st.success("Relatório Geral Gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")
    
    if 'geral_pronto' in st.session_state:
        with open(st.session_state['geral_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name=f"Relatorio_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf")
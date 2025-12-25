import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_vistoria(dados):
    titulo_capa = "RELATÓRIO DE VISTORIA TÉCNICA" if dados['tipo_relatorio'] == "Levantamento" else "RELATÓRIO DE VISITA TÉCNICA"
    
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE VISTORIA TÉCNICA")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal=titulo_capa,
        sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}",
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
    pdf.cell(0, 6, f"Data da Visita: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. INTRODUÇÃO / OBJETIVO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. OBJETIVO / INTRODUÇÃO", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['introducao'], align='J')
    pdf.ln(5)

    # --- 2. CONTEÚDO PRINCIPAL (Híbrido) ---
    pdf.set_font('Barlow', 'B', 12)
    titulo_secao2 = "2. CONSTATAÇÕES POR SETOR" if dados['tipo_relatorio'] == "Levantamento" else "2. DIAGNÓSTICO TÉCNICO E OCORRÊNCIAS"
    pdf.cell(0, 8, titulo_secao2, ln=True)
    pdf.ln(2)

    # MODO A: TABELA (Levantamento/Projeto)
    if dados['tipo_relatorio'] == "Levantamento" and dados['lista_constatacoes']:
        pdf.set_font('Barlow', 'B', 10)
        pdf.set_fill_color(10, 35, 80)
        pdf.set_text_color(255, 255, 255)
        
        # Cabeçalho da Tabela
        pdf.cell(40, 8, "Setor / Local", 1, 0, 'C', True)
        pdf.cell(75, 8, "Situação Atual / Problema", 1, 0, 'C', True)
        pdf.cell(75, 8, "Recomendação Técnica", 1, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Barlow', '', 10)
        
        for item in dados['lista_constatacoes']:
            # Lógica para altura dinâmica da linha (baseada no maior texto)
            # Simplificação: Usamos multi_cell simulado ou fixo. 
            # Aqui vamos usar uma abordagem segura: Imprimir texto corrido se for muito grande
            
            pdf.set_fill_color(245, 245, 245)
            # Salva posição Y inicial
            y_inicio = pdf.get_y()
            
            # Coluna 1
            pdf.set_xy(10, y_inicio)
            pdf.multi_cell(40, 6, item['local'], border='LTRB', align='L', fill=True)
            h1 = pdf.get_y() - y_inicio
            
            # Coluna 2
            pdf.set_xy(50, y_inicio)
            pdf.multi_cell(75, 6, item['problema'], border='LTRB', align='L', fill=False)
            h2 = pdf.get_y() - y_inicio
            
            # Coluna 3
            pdf.set_xy(125, y_inicio)
            pdf.multi_cell(75, 6, item['solucao'], border='LTRB', align='L', fill=False)
            h3 = pdf.get_y() - y_inicio
            
            # Avança para a maior altura para não sobrepor
            altura_max = max(h1, h2, h3)
            pdf.set_y(y_inicio + altura_max)
            
        pdf.ln(5)

    # MODO B: TEXTO LIVRE (Diagnóstico/Manutenção)
    else:
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['diagnostico_texto'], align='J')
        pdf.ln(5)

    # --- 3. RECOMENDAÇÕES GERAIS / MATERIAIS ---
    if dados['recomendacoes']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. RECOMENDAÇÕES E LISTA DE MATERIAIS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['recomendacoes'], align='J')
        pdf.ln(5)

    # --- 4. CONCLUSÃO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. CONCLUSÃO / PARECER FINAL", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    # --- 5. EVIDÊNCIAS (FOTOS) ---
    if dados['lista_fotos']:
        if pdf.get_y() > 220: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "ANEXO FOTOGRÁFICO", ln=True)
        pdf.ln(5)
        
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            legenda = item['legenda']
            
            if os.path.exists(caminho):
                # Verifica quebra de página
                if pdf.get_y() + 90 > 280: pdf.add_page()
                
                # Centraliza
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 10)
                pdf.cell(0, 6, f"Foto {i+1}: {legenda}", align='C', ln=True)
                pdf.ln(8)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Vistoria_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_visita():
    st.subheader("📋 Relatório de Visita Técnica / Vistoria")
    st.caption("Gera relatórios detalhados de diagnóstico ou levantamento de infraestrutura.")

    # --- SELEÇÃO DE MODO ---
    tipo_relatorio = st.radio("Tipo de Relatório:", 
                              ["Diagnóstico de Problemas (Texto Corrido)", "Levantamento de Projeto (Tabela de Setores)"],
                              horizontal=True)
    
    modo = "Diagnostico" if "Texto" in tipo_relatorio else "Levantamento"

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio SQS 113")
        local = st.text_input("Local / Referência", value="Bloco B")
        assunto = st.text_input("Assunto Principal", value="Vistoria de Infraestrutura e CFTV")
    with col2:
        tecnico = st.text_input("Técnico Responsável", value="Luciano Pereira")
        data = st.date_input("Data da Visita").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- 1. INTRODUÇÃO (IA) ---
    st.write("### 1. Introdução / Contexto")
    if "txt_visita_intro" not in st.session_state: st.session_state.txt_visita_intro = ""
    
    rascunho_intro = st.text_area("Objetivo da visita (Rascunho):", 
                                 placeholder="Ex: Fomos chamados para ver pq as câmeras pararam e verificar a cerca elétrica...", height=60)
    
    if st.button("Formalizar Introdução", key="btn_intro"):
        if len(rascunho_intro) > 5:
            with st.spinner("Escrevendo formalmente..."):
                prompt = f"Escreva uma introdução formal para um relatório técnico de {tipo_relatorio}. Contexto: {rascunho_intro}"
                st.session_state.txt_visita_intro = melhorar_texto_com_ia(prompt, "Introdução Relatório")
    
    intro_final = st.text_area("Texto Final (Introdução):", value=st.session_state.txt_visita_intro, height=100)

    # --- 2. CONTEÚDO DINÂMICO ---
    st.markdown("---")
    
    diagnostico_texto_final = ""
    lista_constatacoes = []

    if modo == "Diagnostico":
        st.write("### 2. Diagnóstico Técnico (Ocorrências)")
        if "txt_visita_diag" not in st.session_state: st.session_state.txt_visita_diag = ""
        
        rascunho_diag = st.text_area("O que foi encontrado? (Detalhes):", 
                                    placeholder="Ex: Identificamos curto no disjuntor. O DVR queimou por causa de umidade na sala...", height=150)
        
        if st.button("Formalizar Diagnóstico", key="btn_diag"):
            with st.spinner("Analisando tecnicamente..."):
                prompt = "Reescreva como um diagnóstico técnico detalhado, citando causas prováveis e efeitos observados: " + rascunho_diag
                st.session_state.txt_visita_diag = melhorar_texto_com_ia(prompt, "Diagnóstico Técnico")
        
        diagnostico_texto_final = st.text_area("Texto Final (Diagnóstico):", value=st.session_state.txt_visita_diag, height=200)

    else: # MODO LEVANTAMENTO (TABELA)
        st.write("### 2. Levantamento por Setor (Tabela)")
        st.caption("Adicione linha por linha para criar a tabela de constatações.")
        
        if "tabela_vistoria" not in st.session_state:
            st.session_state.tabela_vistoria = []
            
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 2])
            with c1: t_local = st.text_input("Local/Setor", placeholder="Ex: Portaria")
            with c2: t_prob = st.text_area("Situação Atual", placeholder="Ex: Câmera embaçada...", height=60)
            with c3: t_sol = st.text_area("Recomendação", placeholder="Ex: Trocar por modelo IP...", height=60)
            
            if st.button("➕ Adicionar à Tabela"):
                if t_local and t_prob:
                    st.session_state.tabela_vistoria.append({
                        "local": t_local, "problema": t_prob, "solucao": t_sol
                    })
                    st.rerun()
        
        if st.session_state.tabela_vistoria:
            st.write("**Itens Adicionados:**")
            st.table(st.session_state.tabela_vistoria)
            if st.button("Limpar Tabela"):
                st.session_state.tabela_vistoria = []
                st.rerun()
            lista_constatacoes = st.session_state.tabela_vistoria

    # --- 3. RECOMENDAÇÕES ---
    st.markdown("---")
    st.write("### 3. Recomendações Gerais / Materiais")
    rec_final = st.text_area("Lista de materiais ou ações necessárias:", height=100)

    # --- 4. CONCLUSÃO (IA) ---
    st.write("### 4. Conclusão")
    if "txt_visita_conc" not in st.session_state: st.session_state.txt_visita_conc = ""
    
    rascunho_conc = st.text_area("Resumo final:", placeholder="Ex: O sistema está precário e precisa de reforma urgente...", height=60)
    
    if st.button("Formalizar Conclusão", key="btn_conc"):
        with st.spinner("Concluindo..."):
            prompt = "Escreva um parágrafo de conclusão técnica profissional baseada nisso: " + rascunho_conc
            st.session_state.txt_visita_conc = melhorar_texto_com_ia(prompt, "Conclusão Técnica")
            
    conc_final = st.text_area("Texto Final (Conclusão):", value=st.session_state.txt_visita_conc, height=100)

    # --- 5. FOTOS ---
    st.markdown("---")
    st.write("### 📷 Anexo Fotográfico")
    
    # Upload Múltiplo com Legenda
    uploaded_files = st.file_uploader("Carregar Fotos", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    legendas = {}
    if uploaded_files:
        st.write("Legendas das Fotos:")
        for i, file in enumerate(uploaded_files):
            legendas[file.name] = st.text_input(f"Legenda para {file.name}", value=f"Vista do local {i+1}")

    # --- GERAR ---
    if st.button("Gerar Relatório de Vistoria", type="primary"):
        # Processa Fotos
        lista_fotos_final = []
        if uploaded_files:
            if not os.path.exists("temp"): os.makedirs("temp")
            for file in uploaded_files:
                path = f"temp/vistoria_{file.name}"
                with open(path, "wb") as f: f.write(file.getbuffer())
                lista_fotos_final.append({
                    "caminho": path,
                    "legenda": legendas[file.name]
                })

        dados = {
            "tipo_relatorio": "Levantamento" if modo == "Levantamento" else "Diagnostico",
            "cliente": cliente, "local": local, "assunto": assunto, "tecnico": tecnico, "data": data,
            "introducao": intro_final,
            "diagnostico_texto": diagnostico_texto_final,
            "lista_constatacoes": lista_constatacoes, # Só preenchido se for modo Tabela
            "recomendacoes": rec_final,
            "conclusao": conc_final,
            "lista_fotos": lista_fotos_final
        }

        try:
            arquivo = gerar_pdf_vistoria(dados)
            st.session_state['vistoria_pronto'] = arquivo
            st.success("Relatório Gerado com Sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'vistoria_pronto' in st.session_state:
        with open(st.session_state['vistoria_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF Vistoria", f, file_name=f"Vistoria_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf")
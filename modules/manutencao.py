import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_manutencao(dados):
    
    
    # 1. Lógica do Título da Capa
    if dados['tipo'] == "Corretiva":
        titulo_capa = "RELATÓRIO DE MANUTENÇÃO CORRETIVA"
    elif dados['tipo'] == "Preventiva":
        titulo_capa = "RELATÓRIO DE MANUTENÇÃO PREVENTIVA"
    else:
        titulo_capa = "RELATÓRIO DE VERIFICAÇÃO TÉCNICA" 
    
    pdf = RelatorioBrasfort(titulo=f"{titulo_capa}")
    
    pdf.gerar_capa(
        titulo_principal=titulo_capa,
        sub_titulo=f"Cliente: {dados['cliente']}\nSistema: {dados['sistema']}",
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
    pdf.cell(0, 6, f"Local: {dados['local']} - Data: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- MODO CORRETIVA ---
    if dados['tipo'] == "Corretiva":
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. DESCRIÇÃO DA OCORRÊNCIA / SOLICITAÇÃO", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_ocorrencia'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. ATIVIDADES REALIZADAS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_atividades'], align='J')
        pdf.ln(5)

        if dados['pecas']:
            pdf.set_font('Barlow', 'B', 12)
            pdf.cell(0, 8, "3. PEÇAS SUBSTITUÍDAS / INSTALADAS", ln=True)
            pdf.set_font('Barlow', '', 11)
            pdf.multi_cell(0, 6, dados['pecas'], align='J')
            pdf.ln(5)

    # --- MODO PREVENTIVA OU VERIFICAÇÃO ---
    else:

        titulo_1 = "1. OBJETIVO / O QUE FOI INSPECCIONADO" if dados['tipo'] == "Verificação" else "1. VERIFICAÇÃO GERAL E INSPEÇÃO"
        titulo_2 = "2. PROCEDIMENTOS REALIZADOS E RESULTADOS" if dados['tipo'] == "Verificação" else "2. SITUAÇÕES IDENTIFICADAS / AJUSTES"
        titulo_3 = "3. STATUS DOS EQUIPAMENTOS"
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_1, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_verificacao'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_2, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_situacoes'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_3, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_equipamentos'], align='J')
        pdf.ln(5)

    # --- CONCLUSÃO ---
    pdf.set_font('Barlow', 'B', 12)
    titulo_conclusao = "RESSALVAS E RECOMENDAÇÕES" if dados['tipo'] == "Verificação" else "CONCLUSÃO / STATUS FINAL"
    pdf.cell(0, 8, titulo_conclusao, ln=True)
    
    pdf.set_font('Barlow', 'B', 11)
    if "Operacional" in dados['status'] or "Operante" in dados['status']:
        pdf.set_text_color(0, 150, 0)
    else:
        pdf.set_text_color(200, 100, 0)
    
    pdf.cell(0, 8, f"Status: {dados['status']}", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    # --- FOTOS ---
    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "REGISTRO FOTOGRÁFICO / EVIDÊNCIAS", ln=True)
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
    
    prefixo = "Verificacao" if dados['tipo'] == "Verificação" else "Manutencao"
    nome_arquivo = f"{prefixo}_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_manutencao():
    st.subheader("🛠️ Relatório Técnico")
    
    tipo_manutencao = st.radio("Tipo de Serviço:", 
                               ["Corretiva (Reparo)", "Preventiva (Rotina)", "Verificação Técnica (Testes/Vistoria)"], 
                               horizontal=True)
    
    if "Corretiva" in tipo_manutencao: modo = "Corretiva"
    elif "Preventiva" in tipo_manutencao: modo = "Preventiva"
    else: modo = "Verificação"

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Jardim das Cerejeiras")
        local = st.text_input("Local/Bloco", value="Garagem")
    with col2:
        tecnico = st.text_input("Técnico", value="Seu Nome")
        sistema = st.text_input("Sistema", value="LPR e Semáforos")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")

    texto_ocorrencia_final = ""
    texto_atividades_final = ""
    texto_pecas = ""
    texto_verificacao_final = ""
    texto_situacoes_final = ""
    texto_equipamentos_final = ""

    if modo == "Corretiva":
        st.info("Modo Corretiva: Foco no defeito e reparo.")
        if "txt_man_oco" not in st.session_state: st.session_state.txt_man_oco = ""
        rascunho_oco = st.text_area("1. Qual foi o problema?", height=60, key="rascunho_oco_key")
        if st.button("Formalizar", key="btn_oco"):
            st.session_state.txt_man_oco = melhorar_texto_com_ia(rascunho_oco, "Ocorrência")
        
        # KEY ÚNICA ADICIONADA AQUI
        texto_ocorrencia_final = st.text_area("Texto Final:", value=st.session_state.txt_man_oco, height=80, key="final_oco_key")

        if "txt_man_ativ" not in st.session_state: st.session_state.txt_man_ativ = ""
        rascunho_ativ = st.text_area("2. O que foi feito?", height=80, key="rascunho_ativ_key")
        if st.button("Formalizar Ações", key="btn_ativ"):
            st.session_state.txt_man_ativ = melhorar_texto_com_ia(rascunho_ativ, "Atividades")
        
        # KEY ÚNICA ADICIONADA AQUI
        texto_atividades_final = st.text_area("Texto Final:", value=st.session_state.txt_man_ativ, height=120, key="final_ativ_key")
        
        texto_pecas = st.text_input("3. Peças Utilizadas", key="pecas_key")

    else: # PREVENTIVA OU VERIFICAÇÃO
        st.info(f"Modo {modo}: Foco em testes e diagnóstico.")
        
        label_1 = "1. Objetivo / O que foi inspecionado?" if modo == "Verificação" else "1. Itens Inspecionados"
        if "txt_prev_ver" not in st.session_state: st.session_state.txt_prev_ver = ""
        rascunho_ver = st.text_area(label_1, placeholder="Ex: Verificar semáforos e fluxo...", height=60, key="rascunho_ver_key")
        if st.button("Formalizar Objetivo", key="btn_ver"):
            st.session_state.txt_prev_ver = melhorar_texto_com_ia(rascunho_ver, "Objetivo Técnico")
        
        # KEY ÚNICA ADICIONADA AQUI
        texto_verificacao_final = st.text_area("Texto Final:", value=st.session_state.txt_prev_ver, height=80, key="final_ver_key")

        label_2 = "2. Procedimentos Realizados:" if modo == "Verificação" else "2. Ajustes Realizados:"
        if "txt_prev_sit" not in st.session_state: st.session_state.txt_prev_sit = ""
        rascunho_sit = st.text_area(label_2, placeholder="Ex: Simulação de entrada e saída...", height=80, key="rascunho_sit_key")
        if st.button("Formalizar Procedimentos", key="btn_sit"):
            st.session_state.txt_prev_sit = melhorar_texto_com_ia(rascunho_sit, "Procedimentos Técnicos")
        
        # KEY ÚNICA ADICIONADA AQUI
        texto_situacoes_final = st.text_area("Texto Final:", value=st.session_state.txt_prev_sit, height=100, key="final_sit_key")

        label_3 = "3. Resultados (LPR, Semáforos...):" if modo == "Verificação" else "3. Checagem de Equipamentos:"
        # KEY ÚNICA ADICIONADA AQUI
        texto_equipamentos_final = st.text_area(label_3, value="Sistema LPR: Operante.\nSemáforos: Operando na sequência esperada.", height=80, key="final_equip_key")

    # --- CONCLUSÃO ---
    st.markdown("---")
    label_conc = "4. Ressalvas e Recomendações" if modo == "Verificação" else "Conclusão"
    st.write(f"### {label_conc}")
    
    status_final = st.selectbox("Status Geral:", ["Sistema Operante", "Operante com Ressalvas", "Inoperante"])
    
    if "txt_man_conc" not in st.session_state: st.session_state.txt_man_conc = ""
    rascunho_conc = st.text_area("Texto da Recomendação:", placeholder="Ex: Tempo do semáforo curto...", height=60, key="rascunho_conc_key")
    if st.button("Formalizar Recomendação", key="btn_conc"):
        st.session_state.txt_man_conc = melhorar_texto_com_ia(rascunho_conc, "Recomendação Técnica")
    
    # KEY ÚNICA ADICIONADA AQUI
    conclusao_final = st.text_area("Texto Final:", value=st.session_state.txt_man_conc, height=80, key="final_conc_key")

    upload_fotos = st.file_uploader("Evidências (Vídeo/Foto)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    legendas = {}
    if upload_fotos:
        for f in upload_fotos:
            legendas[f.name] = st.text_input(f"Legenda para {f.name}", value="Registro do teste", key=f"legenda_{f.name}")

    # --- GERAR ---
    if st.button("Gerar Relatório", type="primary"):
        lista_fotos = []
        if upload_fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in upload_fotos:
                path = f"temp/verif_{f.name}"
                with open(path, "wb") as file: file.write(f.getbuffer())
                lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

        dados = {
            "tipo": modo,
            "cliente": cliente, "local": local, "tecnico": tecnico, "sistema": sistema, "data": data,
            "texto_ocorrencia": texto_ocorrencia_final,
            "texto_atividades": texto_atividades_final,
            "pecas": texto_pecas,
            "texto_verificacao": texto_verificacao_final,
            "texto_situacoes": texto_situacoes_final,
            "texto_equipamentos": texto_equipamentos_final,
            "status": status_final,
            "conclusao": conclusao_final,
            "lista_fotos": lista_fotos
        }

        try:
            arquivo = gerar_pdf_manutencao(dados)
            st.session_state['man_pronto'] = arquivo
            st.success("Relatório Gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'man_pronto' in st.session_state:
        with open(st.session_state['man_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name=f"Relatorio_{modo}.pdf")
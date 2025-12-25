import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_manutencao(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    
    # Define título da capa baseado no tipo
    titulo_capa = "RELATÓRIO DE MANUTENÇÃO PREVENTIVA" if dados['tipo'] == "Preventiva" else "RELATÓRIO DE MANUTENÇÃO CORRETIVA"
    
    pdf.gerar_capa(
        titulo_principal=titulo_capa,
        sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}\nSistema: {dados['sistema']}",
        autor=dados['tecnico']
    )
    
    pdf.add_page()
    pdf.ln(20)

    # Cabeçalho Interno
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Local: {dados['local']} - Data: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- MODO CORRETIVA (Foco em Ocorrência -> Solução) ---
    if dados['tipo'] == "Corretiva":
        # 1. Ocorrência
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. DESCRIÇÃO DA OCORRÊNCIA / SOLICITAÇÃO", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_ocorrencia'], align='J')
        pdf.ln(5)

        # 2. Atividades Realizadas
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. ATIVIDADES REALIZADAS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_atividades'], align='J')
        pdf.ln(5)

        # 3. Peças (Se houver)
        if dados['pecas']:
            pdf.set_font('Barlow', 'B', 12)
            pdf.cell(0, 8, "3. PEÇAS SUBSTITUÍDAS / INSTALADAS", ln=True)
            pdf.set_font('Barlow', '', 11)
            pdf.multi_cell(0, 6, dados['pecas'], align='J')
            pdf.ln(5)

    # --- MODO PREVENTIVA (Foco em Verificação -> Status) ---
    else:
        # 1. Verificação Geral
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. VERIFICAÇÃO GERAL E INSPEÇÃO", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_verificacao'], align='J')
        pdf.ln(5)

        # 2. Situações Identificadas
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. SITUAÇÕES IDENTIFICADAS / AJUSTES", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_situacoes'], align='J')
        pdf.ln(5)

        # 3. Checagem de Equipamentos
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. CHECAGEM DE EQUIPAMENTOS (DVR/CENTRAIS)", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_equipamentos'], align='J')
        pdf.ln(5)

    # --- CONCLUSÃO (Comum aos dois) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "CONCLUSÃO / STATUS FINAL", ln=True)
    
    # Cor do Status (Verde se Operacional, Laranja se Parcial)
    pdf.set_font('Barlow', 'B', 11)
    if "Operacional" in dados['status']:
        pdf.set_text_color(0, 150, 0)
    else:
        pdf.set_text_color(200, 100, 0)
    
    pdf.cell(0, 8, f"Status: {dados['status']}", ln=True)
    
    pdf.set_text_color(0, 0, 0) # Reset cor
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    # --- FOTOS (Antes e Depois) ---
    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "REGISTRO FOTOGRÁFICO", ln=True)
        pdf.ln(5)
        
        # Grid de fotos (2 por linha ou 1 centralizada)
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
    
    nome_arquivo = f"Manutencao_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_manutencao():
    st.subheader("🛠️ Relatório de Manutenção")
    
    # Seletor de Tipo (Muda os campos da tela)
    tipo_manutencao = st.radio("Tipo de Serviço:", ["Corretiva (Reparo/Troca)", "Preventiva (Checklist/Vistoria)"], horizontal=True)
    modo = "Corretiva" if "Corretiva" in tipo_manutencao else "Preventiva"

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Green Park")
        local = st.text_input("Local/Bloco", value="Portaria Principal")
    with col2:
        tecnico = st.text_input("Técnico", value="Luciano Pereira")
        sistema = st.text_input("Sistema (Ex: Interfone/CFTV)", value="CFTV")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- CAMPOS DINÂMICOS ---
    
    texto_ocorrencia_final = ""
    texto_atividades_final = ""
    texto_pecas = ""
    
    texto_verificacao_final = ""
    texto_situacoes_final = ""
    texto_equipamentos_final = ""

    if modo == "Corretiva":
        st.info("Modo Corretiva: Foco no defeito relatado e na solução aplicada.")
        
        # 1. Ocorrência
        if "txt_man_oco" not in st.session_state: st.session_state.txt_man_oco = ""
        rascunho_oco = st.text_area("1. Qual foi o problema/solicitação?", placeholder="Ex: Interfone do 111 mudo...", height=60)
        if st.button("Formalizar Ocorrência", key="btn_oco"):
            st.session_state.txt_man_oco = melhorar_texto_com_ia("Formalize este defeito relatado: " + rascunho_oco, "Ocorrência Técnica")
        texto_ocorrencia_final = st.text_area("Texto Final (Ocorrência):", value=st.session_state.txt_man_oco, height=80)

        # 2. Atividades
        if "txt_man_ativ" not in st.session_state: st.session_state.txt_man_ativ = ""
        rascunho_ativ = st.text_area("2. O que foi feito?", placeholder="Ex: Testei a fiação, troquei o conector e configurei o ramal...", height=80)
        if st.button("Formalizar Atividades", key="btn_ativ"):
            st.session_state.txt_man_ativ = melhorar_texto_com_ia("Descreva tecnicamente estas atividades de reparo: " + rascunho_ativ, "Atividades Realizadas")
        texto_atividades_final = st.text_area("Texto Final (Atividades):", value=st.session_state.txt_man_ativ, height=120)

        # 3. Peças
        texto_pecas = st.text_input("3. Peças Utilizadas (Opcional)", placeholder="Ex: 1 Fonte 12V, 2 Conectores BNC")

    else: # PREVENTIVA
        st.info("Modo Preventiva: Foco na inspeção geral e checklist.")
        
        # 1. Verificação Geral
        if "txt_prev_ver" not in st.session_state: st.session_state.txt_prev_ver = ""
        rascunho_ver = st.text_area("1. O que foi inspecionado?", placeholder="Ex: Verifiquei todas as câmeras dos blocos A e B...", height=60)
        if st.button("Formalizar Inspeção", key="btn_ver"):
            st.session_state.txt_prev_ver = melhorar_texto_com_ia("Descreva esta rotina de inspeção preventiva: " + rascunho_ver, "Inspeção Técnica")
        texto_verificacao_final = st.text_area("Texto Final (Verificação):", value=st.session_state.txt_prev_ver, height=80)

        # 2. Situações
        if "txt_prev_sit" not in st.session_state: st.session_state.txt_prev_sit = ""
        rascunho_sit = st.text_area("2. Problemas encontrados / Ajustes:", placeholder="Ex: Câmera 3 suja (limpei), suporte quebrado (troquei)...", height=80)
        if st.button("Formalizar Ajustes", key="btn_sit"):
            st.session_state.txt_prev_sit = melhorar_texto_com_ia("Relate estas situações encontradas e ajustes feitos: " + rascunho_sit, "Relatório de Ajustes")
        texto_situacoes_final = st.text_area("Texto Final (Situações):", value=st.session_state.txt_prev_sit, height=100)

        # 3. Equipamentos
        texto_equipamentos_final = st.text_area("3. Status dos Equipamentos (DVR/NVR)", value="Todos os equipamentos (DVRs, Fontes e Switches) operam dentro dos parâmetros normais, sem erros de disco ou rede.")

    # --- CONCLUSÃO E FOTOS (Comum) ---
    st.markdown("---")
    st.write("### ✅ Conclusão e Evidências")
    
    status_final = st.selectbox("Status Final:", ["Sistema 100% Operacional", "Operacional com Ressalvas", "Parcialmente Inoperante"])
    
    if "txt_man_conc" not in st.session_state: st.session_state.txt_man_conc = ""
    rascunho_conc = st.text_area("Considerações Finais:", placeholder="Ex: Tudo funcionando, cliente testou e aprovou.", height=60)
    if st.button("Formalizar Conclusão", key="btn_conc"):
        st.session_state.txt_man_conc = melhorar_texto_com_ia("Faça uma conclusão técnica curta: " + rascunho_conc, "Conclusão")
    conclusao_final = st.text_area("Texto Final (Conclusão):", value=st.session_state.txt_man_conc, height=80)

    upload_fotos = st.file_uploader("Fotos (Antes/Depois)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    legendas = {}
    if upload_fotos:
        for f in upload_fotos:
            legendas[f.name] = st.text_input(f"Legenda para {f.name}", value="Registro da manutenção")

    # --- GERAR ---
    if st.button("Gerar Relatório de Manutenção", type="primary"):
        lista_fotos = []
        if upload_fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in upload_fotos:
                path = f"temp/man_{f.name}"
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
            st.success("Relatório de Manutenção Gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'man_pronto' in st.session_state:
        with open(st.session_state['man_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF Manutenção", f, file_name="Relatorio_Manutencao.pdf")
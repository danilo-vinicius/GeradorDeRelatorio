import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_ocorrencia(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Relatório de Ocorrência Técnica",
        sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}\nData: {dados['data']}",
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

    # --- 1. DESCRIÇÃO DA OCORRÊNCIA (A História) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. DESCRIÇÃO DA OCORRÊNCIA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao'], align='J')
    pdf.ln(5)

    # --- 2. IMPACTO OPERACIONAL (Consequências) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. IMPACTO OPERACIONAL E SISTEMAS AFETADOS", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['impacto'], align='J')
    pdf.ln(5)

    # --- 3. AÇÕES EXECUTADAS (O que foi feito na hora) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. AÇÕES TÉCNICAS EXECUTADAS", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['acoes'], align='J')
    pdf.ln(5)

    # --- 4. ESTADO ATUAL E PRÓXIMOS PASSOS ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. ESTADO ATUAL E RECOMENDAÇÕES", ln=True)
    pdf.set_font('Barlow', '', 11)
    
    # Texto combinado de status + recomendação para ficar fluido
    texto_final = f"Situação Atual: {dados['status']}\n\nRecomendação Definitiva: {dados['recomendacao']}"
    pdf.multi_cell(0, 6, texto_final, align='J')
    pdf.ln(10)

    # --- 5. EVIDÊNCIAS FOTOGRÁFICAS ---
    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "5. REGISTRO FOTOGRÁFICO", ln=True)
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
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"Foto {i+1}: {legenda}", align='C', ln=True)
                pdf.ln(8)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Ocorrencia_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_ocorrencia():
    st.subheader("⚠️ Relatório de Ocorrência Técnica")
    st.caption("Para incidentes, danos por terceiros e falhas críticas.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Usina São Pedro")
        local = st.text_input("Local Afetado", value="Perímetro Externo / CPD")
    with col2:
        tecnico = st.text_input("Responsável Técnico", value="Luciano Pereira")
        data = st.date_input("Data do Ocorrido").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- 1. A HISTÓRIA (DESCRIÇÃO) ---
    st.write("### 1. O que aconteceu?")
    if "txt_oco_desc" not in st.session_state: st.session_state.txt_oco_desc = ""
    
    rascunho_desc = st.text_area("Relato do incidente (Rascunho):", 
                                placeholder="Ex: Pessoal da obra passou com o trator e cortou a fibra óptica perto do poste 3...", height=70)
    
    if st.button("Formalizar Relato", key="btn_desc"):
        if len(rascunho_desc) > 5:
            with st.spinner("Escrevendo narrativa técnica..."):
                prompt = "Reescreva este relato de incidente técnico de forma formal e imparcial: " + rascunho_desc
                st.session_state.txt_oco_desc = melhorar_texto_com_ia(prompt, "Relato de Incidente")
    
    desc_final = st.text_area("Texto Final (Descrição):", value=st.session_state.txt_oco_desc, height=100)

    # --- 2. O IMPACTO (CONSEQUÊNCIAS) ---
    st.write("### 2. O que parou de funcionar? (Impacto)")
    if "txt_oco_imp" not in st.session_state: st.session_state.txt_oco_imp = ""
    
    rascunho_imp = st.text_area("Falhas geradas:", 
                               placeholder="Ex: Perdemos acesso a 4 câmeras speed dome e o alarme do galpão ficou offline...", height=60)
    
    if st.button("Formalizar Impacto", key="btn_imp"):
        with st.spinner("Listando consequências..."):
            prompt = "Descreva tecnicamente o impacto operacional desta falha: " + rascunho_imp
            st.session_state.txt_oco_imp = melhorar_texto_com_ia(prompt, "Impacto Técnico")
            
    imp_final = st.text_area("Texto Final (Impacto):", value=st.session_state.txt_oco_imp, height=80)

    # --- 3. AÇÕES EXECUTADAS ---
    st.markdown("---")
    st.write("### 3. Ações Imediatas (Contenção)")
    if "txt_oco_acao" not in st.session_state: st.session_state.txt_oco_acao = ""
    
    rascunho_acao = st.text_area("O que foi feito na hora?", 
                                placeholder="Ex: Fizemos uma emenda provisória na fibra e colocamos um chip GPRS no alarme...", height=60)
    
    if st.button("Formalizar Ações", key="btn_acao"):
        with st.spinner("Descrevendo procedimentos..."):
            prompt = "Descreva tecnicamente as ações corretivas ou paliativas realizadas: " + rascunho_acao
            st.session_state.txt_oco_acao = melhorar_texto_com_ia(prompt, "Procedimentos Técnicos")
            
    acao_final = st.text_area("Texto Final (Ações):", value=st.session_state.txt_oco_acao, height=80)

    # --- 4. STATUS E RECOMENDAÇÃO ---
    c1, c2 = st.columns(2)
    with c1:
        status_atual = st.selectbox("Status Atual do Sistema:", 
                     ["Operacional (Resolvido)", 
                      "Parcialmente Operacional (Provisório)", 
                      "Inoperante (Aguardando Peças/Serviço)"])
    with c2:
        recomendacao = st.text_input("O que precisa ser feito agora?", placeholder="Ex: Troca de 200m de cabo óptico.")

    # --- 5. FOTOS ---
    st.markdown("---")
    st.write("### 📷 Evidências (Danos e Reparos)")
    
    uploaded_files = st.file_uploader("Fotos do incidente", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    legendas = {}
    if uploaded_files:
        for f in uploaded_files:
            legendas[f.name] = st.text_input(f"Legenda para {f.name}", value="Detalhe da avaria")

    # --- GERAR ---
    if st.button("Gerar Relatório de Ocorrência", type="primary"):
        lista_fotos = []
        if uploaded_files:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in uploaded_files:
                path = f"temp/oco_{f.name}"
                with open(path, "wb") as file: file.write(f.getbuffer())
                lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

        dados = {
            "cliente": cliente, "local": local, "tecnico": tecnico, "data": data,
            "descricao": desc_final, "impacto": imp_final, "acoes": acao_final,
            "status": status_atual, "recomendacao": recomendacao,
            "lista_fotos": lista_fotos
        }

        try:
            arquivo = gerar_pdf_ocorrencia(dados)
            st.session_state['oco_pronto'] = arquivo
            st.success("Relatório de Ocorrência Gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'oco_pronto' in st.session_state:
        with open(st.session_state['oco_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF Ocorrência", f, file_name="Relatorio_Ocorrencia.pdf")
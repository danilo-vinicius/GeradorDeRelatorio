import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF DA OS ---
def gerar_pdf_os(dados):
    pdf = RelatorioBrasfort(titulo="ORDEM DE SERVIÇO")
    
    # Capa simplificada ou cabeçalho direto? 
    # OS geralmente é documento de uma página só (ou continuação).
    # Vamos fazer direto sem capa, para parecer uma OS de sistema mesmo.
    pdf.add_page()
    
    # --- CABEÇALHO PRO (Estilo PerformanceLab mas mais bonito) ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(200, 200, 200)
    
    # Bloco 1: Informações Básicas
    pdf.set_font('Barlow', 'B', 14)
    pdf.cell(0, 10, f"ORDEM DE SERVIÇO Nº {dados['numero_os']}", ln=True, align='R')
    pdf.ln(2)
    
    # Bloco 2: Dados do Cliente (Caixa Cinza)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "DADOS DO CLIENTE", ln=True, fill=True)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(15, 6, "Cliente:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, dados['cliente'], 0, 1)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(15, 6, "Local:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.multi_cell(0, 6, dados['local']) # Multi-cell caso o endereço seja longo
    
    pdf.ln(4)

    # Bloco 3: Dados da O.S. (Caixa Cinza)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "DADOS TÉCNICOS DA O.S.", ln=True, fill=True)
    
    # Linha 1
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(25, 6, "Classificação:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(60, 6, dados['classificacao'], 0, 0)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(15, 6, "Tipo:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, dados['tipo_servico'], 0, 1)
    
    # Linha 2
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(25, 6, "Equipamento:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(60, 6, dados['equipamento'], 0, 0)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(30, 6, "Data Atendimento:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, f"{dados['data']} - {dados['hora_inicio']} às {dados['hora_fim']}", 0, 1)
    
    # Necessidade (O problema relatado)
    pdf.ln(2)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "Necessidade / Solicitação:", ln=True)
    pdf.set_font('Barlow', '', 10)
    pdf.multi_cell(0, 6, dados['necessidade'], border='L')
    pdf.ln(5)

    # --- 4. RELATO TÉCNICO (Ação Realizada) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "HISTÓRICO DE AÇÕES REALIZADAS", ln=True, fill=True)
    pdf.ln(2)
    
    # Simula a tabela do PerformanceLab mas com texto corrido organizado
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['relato_tecnico'], border=1, align='J')
    pdf.ln(5)

    # --- 5. PENDÊNCIAS OU OBSERVAÇÕES ---
    if dados['observacoes']:
        pdf.set_font('Barlow', 'B', 10)
        pdf.cell(0, 6, "Observações / Pendências:", ln=True)
        pdf.set_font('Barlow', '', 10)
        pdf.multi_cell(0, 6, dados['observacoes'], border='L')
        pdf.ln(5)

    # --- 6. FOTOS ---
    if dados['lista_fotos']:
        pdf.ln(5)
        pdf.set_font('Barlow', 'B', 10)
        pdf.cell(0, 6, "ANEXOS / EVIDÊNCIAS", ln=True, fill=True)
        pdf.ln(5)
        
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            legenda = item['legenda']
            
            if os.path.exists(caminho):
                if pdf.get_y() + 90 > 280: pdf.add_page()
                
                # Centraliza
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                pdf.ln(2)
                
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"Anexo {i+1}: {legenda}", align='C', ln=True)
                pdf.ln(8)

    # --- 7. ASSINATURAS ---
    # Garante que as assinaturas fiquem no final
    if pdf.get_y() > 240: pdf.add_page()
    
    pdf.set_y(-50)
    pdf.set_font('Barlow', '', 10)
    
    # Linha Técnico
    pdf.cell(90, 6, "___________________________________", 0, 0, 'C')
    pdf.cell(10, 6, "", 0, 0)
    pdf.cell(90, 6, "___________________________________", 0, 1, 'C')
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(90, 5, dados['tecnico'], 0, 0, 'C')
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, "Responsável Cliente", 0, 1, 'C')
    
    pdf.set_font('Barlow', '', 9)
    pdf.cell(90, 5, "Técnico Brasfort", 0, 0, 'C')
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, "Aceite dos Serviços", 0, 1, 'C')

    nome_arquivo = f"OS_{dados['numero_os']}_{dados['cliente'].split()[0]}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_os():
    st.subheader("🛠️ Emissor de Ordem de Serviço (Backup)")
    st.caption("Gere OSs padronizadas em caso de instabilidade do sistema principal.")

    col_os1, col_os2, col_os3 = st.columns([1, 2, 1])
    with col_os1:
        num_os = st.text_input("Nº da O.S.", value="1850")
    with col_os2:
        classificacao = st.selectbox("Classificação:", ["SEGURANÇA ELETRÔNICA", "INFRAESTRUTURA", "TI / REDES"])
    with col_os3:
        tipo_servico = st.selectbox("Tipo:", ["Manutenção Corretiva", "Manutenção Preventiva", "Instalação", "Verificação/Orçamento"])

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Brasfort Adm")
        local = st.text_input("Local / Site", value="Sede - SIA Trecho 3")
    with col2:
        equipamento = st.text_input("Equipamento Alvo", value="CFTV Geral")
        tecnico = st.text_input("Técnico Responsável", value="Luciano Pereira")

    c_data, c_h_ini, c_h_fim = st.columns(3)
    data = c_data.date_input("Data").strftime("%d/%m/%Y")
    hora_ini = c_h_ini.text_input("Hora Início", value="08:00")
    hora_fim = c_h_fim.text_input("Hora Fim", value="10:00")

    st.markdown("---")

    # --- 1. NECESSIDADE ---
    st.write("**1. Necessidade / Problema Relatado**")
    if "txt_os_nec" not in st.session_state: st.session_state.txt_os_nec = ""
    
    rascunho_nec = st.text_area("O que precisa ser feito?", placeholder="Ex: Instalar motor no portão B ou Verificar câmera 3 offline...", height=60)
    if st.button("Formalizar Necessidade", key="btn_os_nec"):
        st.session_state.txt_os_nec = melhorar_texto_com_ia("Formalize esta solicitação de serviço de forma breve: " + rascunho_nec, "Solicitação de OS")
    
    necessidade_final = st.text_area("Texto Final (Necessidade):", value=st.session_state.txt_os_nec, height=70)

    # --- 2. RELATO TÉCNICO ---
    st.write("**2. Relato Técnico (Ação Realizada)**")
    if "txt_os_relato" not in st.session_state: st.session_state.txt_os_relato = ""
    
    rascunho_relato = st.text_area("O que foi executado?", 
                                  placeholder="Ex: Passei o cabo, fixei o motor, configurei a central e testei os controles...", height=100)
    
    if st.button("Formalizar Relato Técnico", key="btn_os_rel"):
        with st.spinner("Escrevendo tecnicamente..."):
            prompt = f"Descreva tecnicamente as ações realizadas nesta OS de {tipo_servico}. Ações: {rascunho_relato}"
            st.session_state.txt_os_relato = melhorar_texto_com_ia(prompt, "Relato Técnico de OS")
            
    relato_final = st.text_area("Texto Final (Relato):", value=st.session_state.txt_os_relato, height=150)

    # --- 3. OBSERVAÇÕES ---
    observacoes = st.text_input("Observações Gerais (Opcional)", placeholder="Ex: Faltou acabamento por falta de material.")

    # --- 4. FOTOS ---
    st.markdown("---")
    uploaded_files = st.file_uploader("Evidências (Fotos)", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    # --- GERAR ---
    if st.button("Emitir Ordem de Serviço", type="primary"):
        lista_fotos = []
        if uploaded_files:
            if not os.path.exists("temp"): os.makedirs("temp")
            for f in uploaded_files:
                path = f"temp/os_{f.name}"
                with open(path, "wb") as file: file.write(f.getbuffer())
                lista_fotos.append({"caminho": path, "legenda": "Evidência de Execução"})

        dados = {
            "numero_os": num_os, "classificacao": classificacao, "tipo_servico": tipo_servico,
            "cliente": cliente, "local": local, "equipamento": equipamento, "tecnico": tecnico,
            "data": data, "hora_inicio": hora_ini, "hora_fim": hora_fim,
            "necessidade": necessidade_final,
            "relato_tecnico": relato_final,
            "observacoes": observacoes,
            "lista_fotos": lista_fotos
        }

        try:
            arquivo = gerar_pdf_os(dados)
            st.session_state['os_pronta'] = arquivo
            st.success(f"OS {num_os} emitida com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'os_pronta' in st.session_state:
        with open(st.session_state['os_pronta'], "rb") as f:
            st.download_button("📥 Baixar OS PDF", f, file_name=f"OS_{num_os}.pdf")
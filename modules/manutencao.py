import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_manutencao(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE MANUTENÇÃO TÉCNICA")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Relatório de Manutenção",
        sub_titulo=f"Cliente: {dados['cliente']}\nServiço: {dados['tipo_servico']}",
        autor="Departamento Técnico"
    )
    
    pdf.add_page()
    
    # --- DADOS DO CLIENTE ---
    pdf.set_fill_color(245, 245, 245)
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    pdf.set_y(pdf.get_y() + 5)
    
    pdf.set_x(15)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(20, 6, "Cliente:", align='L')
    pdf.set_font('Barlow', '', 12)
    pdf.cell(100, 6, dados['cliente'], ln=True)
    
    pdf.set_x(15)
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(20, 6, "Data:", align='L')
    pdf.set_font('Barlow', '', 12)
    pdf.cell(100, 6, dados['data'], ln=True)
    pdf.ln(10)

    # --- EQUIPAMENTO ALVO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Equipamento / Sistema Atendido", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.cell(0, 8, dados['equipamento'], border='B', ln=True)
    pdf.ln(5)

    # --- PROCEDIMENTOS REALIZADOS ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Descrição dos Serviços Executados", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao_servico'])
    pdf.ln(5)

    # --- STATUS FINAL ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(40, 8, "Status Final:", align='L')
    
    # Colore o status (Verde se OK, Laranja se Parcial)
    if "Operacional" in dados['status']:
        pdf.set_text_color(0, 150, 0) # Verde
    else:
        pdf.set_text_color(200, 100, 0) # Laranja
        
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, dados['status'], ln=True)
    pdf.set_text_color(0, 0, 0) # Reset
    pdf.ln(10)

    # --- FOTOS (ANTES E DEPOIS) ---
    if dados['foto_antes'] or dados['foto_depois']:
        if pdf.get_y() > 180: pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. Registro Fotográfico", ln=True)
        pdf.ln(2)
        
        y_fotos = pdf.get_y()
        
        # Lógica para colocar lado a lado se tiver as duas
        if dados['foto_antes'] and dados['foto_depois']:
            # Foto Antes (Esquerda)
            pdf.set_font('Barlow', 'B', 10)
            pdf.text(30, y_fotos - 2, "ANTES")
            if os.path.exists(dados['foto_antes']):
                pdf.image(dados['foto_antes'], x=10, y=y_fotos, w=90)
            
            # Foto Depois (Direita)
            pdf.text(130, y_fotos - 2, "DEPOIS")
            if os.path.exists(dados['foto_depois']):
                pdf.image(dados['foto_depois'], x=110, y=y_fotos, w=90)
                
            pdf.ln(70) # Pula a altura das fotos
            
        else:
            # Só tem uma foto, centraliza
            foto_unica = dados['foto_antes'] if dados['foto_antes'] else dados['foto_depois']
            titulo = "Registro Visual"
            if os.path.exists(foto_unica):
                pdf.image(foto_unica, x=55, w=100)
                pdf.ln(80)

    # Assinatura
    pdf.bloco_assinatura("Técnico Responsável")
    
    nome_arquivo = f"Manutencao_{dados['cliente'].split()[0]}_{dados['equipamento'].split()[0]}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_manutencao():
    st.subheader("🔧 Relatório de Manutenção / Conserto")
    st.caption("Registre limpezas, reparos e manutenções preventivas.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Top Life")
        tipo_servico = st.text_input("Tipo de Serviço", value="Manutenção Preventiva")
    with col2:
        equipamento = st.text_input("Equipamento Atendido", value="Central de Interfonia CP 112")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("**Descrição do Serviço**")

    # --- IA ---
    if "texto_manutencao" not in st.session_state:
        st.session_state.texto_manutencao = ""

    rascunho = st.text_area("Rascunho (O que foi feito?):", 
                           placeholder="Ex: Limpei a placa que tava com poeira, apertei os parafusos e testei os ramais...",
                           height=70)

    if st.button("✨ Melhorar Texto (IA)", type="secondary"):
        if len(rascunho) > 5:
            with st.spinner("Gerando descrição técnica..."):
                # Usamos um prompt levemente diferente na função da IA (passando o tipo)
                texto = melhorar_texto_com_ia(rascunho, "Relatório de Manutenção")
                st.session_state.texto_manutencao = texto
        else:
            st.warning("Digite o rascunho primeiro.")

    descricao_final = st.text_area("Texto Final:", value=st.session_state.texto_manutencao, height=120)
    
    # Status
    status = st.selectbox("Status Final do Equipamento", 
                          ["Operacional (Funcionando)", "Operacional com Ressalvas", "Parcialmente Operacional", "Aguardando Peças"])

    # Fotos Lado a Lado
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        f_antes = st.file_uploader("Foto ANTES (Opcional)", type=['jpg', 'png'])
    with c2:
        f_depois = st.file_uploader("Foto DEPOIS (Opcional)", type=['jpg', 'png'])

    if st.button("Gerar Relatório de Manutenção", type="primary"):
        # Salva fotos
        path_antes = ""
        path_depois = ""
        
        if not os.path.exists("temp"): os.makedirs("temp")
        
        if f_antes:
            path_antes = f"temp/antes_{f_antes.name}"
            with open(path_antes, "wb") as f: f.write(f_antes.getbuffer())
            
        if f_depois:
            path_depois = f"temp/depois_{f_depois.name}"
            with open(path_depois, "wb") as f: f.write(f_depois.getbuffer())

        dados = {
            "cliente": cliente,
            "tipo_servico": tipo_servico,
            "equipamento": equipamento,
            "data": data,
            "descricao_servico": descricao_final,
            "status": status,
            "foto_antes": path_antes,
            "foto_depois": path_depois
        }

        try:
            arquivo = gerar_pdf_manutencao(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Relatório gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")
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
    
    # Cabeçalho
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

    # Equipamento
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Equipamento / Sistema Atendido", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.cell(0, 8, dados['equipamento'], border='B', ln=True)
    pdf.ln(5)

    # Descrição
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Descrição dos Serviços Executados", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['descricao_servico'])
    pdf.ln(5)

    # Status
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(40, 8, "Status Final:", align='L')
    
    if "Operacional" in dados['status']:
        pdf.set_text_color(0, 150, 0)
    else:
        pdf.set_text_color(200, 100, 0)
        
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, dados['status'], ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Fotos
    if dados['foto_antes'] or dados['foto_depois']:
        if pdf.get_y() > 180: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. Registro Fotográfico", ln=True)
        pdf.ln(2)
        y_fotos = pdf.get_y()
        
        if dados['foto_antes'] and dados['foto_depois']:
            pdf.set_font('Barlow', 'B', 10)
            pdf.text(30, y_fotos - 2, "ANTES")
            if os.path.exists(dados['foto_antes']):
                pdf.image(dados['foto_antes'], x=10, y=y_fotos, w=90)
            pdf.text(130, y_fotos - 2, "DEPOIS")
            if os.path.exists(dados['foto_depois']):
                pdf.image(dados['foto_depois'], x=110, y=y_fotos, w=90)
            pdf.ln(70) 
        else:
            foto_unica = dados['foto_antes'] if dados['foto_antes'] else dados['foto_depois']
            if os.path.exists(foto_unica):
                pdf.image(foto_unica, x=55, w=100)
                pdf.ln(80)

    pdf.bloco_assinatura("Técnico Responsável")
    
    nome_arquivo = f"Manutencao_{dados['cliente'].split()[0]}_{dados['equipamento'].split()[0]}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_manutencao():
    st.subheader("🔧 Relatório de Manutenção / Conserto")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Top Life")
        tipo_servico = st.text_input("Tipo de Serviço", value="Manutenção Preventiva")

    with col2:
        # VOLTAMOS AO SIMPLES: TEXT INPUT
        equipamento = st.text_input("Equipamento Atendido", value="DVR Intelbras")
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("**Descrição do Serviço**")

    # IA TEXTUALIZAÇÃO
    if "texto_manutencao" not in st.session_state:
        st.session_state.texto_manutencao = ""

    rascunho = st.text_area("Rascunho (Digite de qualquer jeito):", height=70)

    if st.button("✨ Melhorar Texto com IA", type="secondary"):
        if len(rascunho) > 3:
            with st.spinner("Reescrevendo de forma técnica..."):
                texto = melhorar_texto_com_ia(rascunho, "Relatório de Manutenção")
                st.session_state.texto_manutencao = texto
        else:
            st.warning("Digite algo no rascunho.")

    descricao_final = st.text_area("Texto Final:", value=st.session_state.texto_manutencao, height=120)
    
    status = st.selectbox("Status Final", ["Operacional", "Operacional com Ressalvas", "Parcial", "Inoperante"])

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1: f_antes = st.file_uploader("Foto ANTES", type=['jpg', 'png'])
    with c2: f_depois = st.file_uploader("Foto DEPOIS", type=['jpg', 'png'])

    if st.button("Gerar Relatório PDF", type="primary"):
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
            st.success("Relatório gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
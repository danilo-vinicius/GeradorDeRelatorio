import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- FUNÇÃO QUE GERA O PDF (MOTOR) ---
def gerar_pdf_equipamento(dados):
    # 1. Instancia a classe base (define o título que vai no cabeçalho das pág. internas)
    pdf = RelatorioBrasfort(titulo="LAUDO TÉCNICO DE EQUIPAMENTO")

    # 2. GERA A CAPA (FOLHA DE ROSTO)
    # A capa vem antes de tudo. Personalize o 'autor' se quiser.
    pdf.gerar_capa(
        titulo_principal="Laudo Técnico de Avaria",
        sub_titulo=f"Cliente: {dados['cliente']}\nEquipamento: {dados['equipamento']}",
        autor="Departamento Técnico" 
    )

    # 3. Adiciona a primeira página de conteúdo (página 2)
    pdf.add_page()
    
    # --- BLOCO DE DADOS DO CLIENTE ---
    # Fundo cinza suave
    pdf.set_fill_color(245, 245, 245)
    # Desenha um retângulo: x=10, y=atual, w=190, h=25
    pdf.rect(10, pdf.get_y(), 190, 25, 'F')
    
    # Move cursor para dentro do retângulo
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
    
    pdf.ln(10) # Espaço após o bloco do cliente

    # --- TABELA DE IDENTIFICAÇÃO DO EQUIPAMENTO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Identificação do Equipamento", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    # Cabeçalho da tabela com fundo cinza mais escuro
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 8, "Equipamento", border=1, fill=True)
    pdf.cell(60, 8, "Nº Série / Patrimônio", border=1, fill=True, ln=True)
    
    # Dados da tabela
    pdf.cell(80, 8, dados['equipamento'], border=1)
    pdf.cell(60, 8, dados['serial'], border=1, ln=True)
    pdf.ln(5)

    # --- DIAGNÓSTICO TÉCNICO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Análise Técnica e Defeitos", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    # Multi_cell para quebrar o texto longo automaticamente
    pdf.multi_cell(0, 6, dados['diagnostico'])
    pdf.ln(5)
    
    # --- CONCLUSÃO ---
    pdf.set_font('Barlow', 'B', 12)
    
    # Se a conclusão for troca, destaca em vermelho
    if "Troca" in dados['conclusao']:
        pdf.set_text_color(200, 0, 0)
    
    pdf.cell(0, 8, f"Conclusão: {dados['conclusao']}", ln=True)
    pdf.set_text_color(0, 0, 0) # Volta para preto
    pdf.ln(5)

    # --- EVIDÊNCIA FOTOGRÁFICA ---
    if dados['foto_avaria'] and os.path.exists(dados['foto_avaria']):
        # Se não couber na página, cria uma nova
        if pdf.get_y() > 200: 
            pdf.add_page()
        
        pdf.set_font('Barlow', 'B', 11)
        pdf.cell(0, 8, "Evidência Fotográfica:", ln=True)
        try:
            # Centraliza a imagem (x=45 para largura de 120 numa pág A4)
            pdf.image(dados['foto_avaria'], x=45, w=120)
        except:
            pdf.cell(0, 10, "[Erro ao inserir imagem]", ln=True)

    # --- ASSINATURA ---
    pdf.bloco_assinatura("Técnico de Suporte")
    
    # Salva o arquivo
    nome_arquivo = f"Laudo_{dados['cliente'].split()[0]}_{dados['equipamento']}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE (FORMULÁRIO DO STREAMLIT) ---
def renderizar_formulario_equipamento():
    st.subheader("🛠️ Laudo de Avaria (com IA)")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Green Park")
        equipamento = st.text_input("Equipamento", value="DVR Intelbras MHDX")
    with col2:
        serial = st.text_input("Nº Série", value="XYZ-99998888")
        data = st.date_input("Data da Análise").strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("**Diagnóstico Técnico**")

    # Inicializa variavel para guardar o texto da IA
    if "texto_diagnostico" not in st.session_state:
        st.session_state.texto_diagnostico = ""

    # Área de rascunho
    rascunho = st.text_area("Rascunho / Relato Informal:", 
                           placeholder="Ex: A fonte queimou e a placa ta cheia de zinabre...",
                           height=70)

    # Botão da IA
    if st.button("✨ Melhorar com IA", type="secondary"):
        if len(rascunho) > 5:
            with st.spinner("Consultando base de conhecimento Brasfort..."):
                texto_melhorado = melhorar_texto_com_ia(rascunho, "Laudo de Avaria")
                st.session_state.texto_diagnostico = texto_melhorado
        else:
            st.warning("Escreva algo no rascunho primeiro.")

    # Campo final (editável)
    diagnostico_final = st.text_area("Texto Final (Para o PDF):", 
                                     value=st.session_state.texto_diagnostico, 
                                     height=150)
    
    conclusao = st.selectbox("Parecer Final", 
                             ["Troca Imediata", "Envio para RMA", "Equipamento Operacional", "Mau Uso"])

    foto = st.file_uploader("Foto da Avaria", type=['jpg', 'png'])

    # Botão de Gerar
    if st.button("Gerar Laudo PDF", type="primary"):
        caminho_foto = ""
        # Salva foto temporariamente
        if foto:
            if not os.path.exists("temp"): os.makedirs("temp")
            caminho_foto = f"temp/{foto.name}"
            with open(caminho_foto, "wb") as f:
                f.write(foto.getbuffer())

        dados = {
            "cliente": cliente,
            "data": data,
            "equipamento": equipamento,
            "serial": serial,
            "diagnostico": diagnostico_final,
            "conclusao": conclusao,
            "foto_avaria": caminho_foto
        }

        try:
            arquivo = gerar_pdf_equipamento(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Laudo gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")
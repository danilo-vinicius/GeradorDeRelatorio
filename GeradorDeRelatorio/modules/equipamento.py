import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort

def gerar_pdf_equipamento(dados):
    # Definimos o título aqui na criação
    pdf = RelatorioBrasfort(titulo="LAUDO TÉCNICO DE EQUIPAMENTO")
    pdf.add_page()
    
    # --- DADOS DO CLIENTE (Bloco cinza leve para destacar) ---
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

    # --- TABELA DO EQUIPAMENTO ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Identificação do Equipamento", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    # Cabeçalho da tabela
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 8, "Equipamento", border=1, fill=True)
    pdf.cell(60, 8, "Nº Série / Patrimônio", border=1, fill=True, ln=True)
    
    # Linha de dados
    pdf.cell(80, 8, dados['equipamento'], border=1)
    pdf.cell(60, 8, dados['serial'], border=1, ln=True)
    pdf.ln(5)

    # --- DESCRIÇÃO TÉCNICA (Baseado no Green Park) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. Análise Técnica e Defeitos", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['diagnostico'])
    pdf.ln(5)
    
    # --- CONCLUSÃO ---
    pdf.set_font('Barlow', 'B', 12)
    # Se a conclusão for "Troca", destacamos em vermelho, senão preto
    if "Troca" in dados['conclusao']:
        pdf.set_text_color(200, 0, 0)
    
    pdf.cell(0, 8, f"Conclusão: {dados['conclusao']}", ln=True)
    pdf.set_text_color(0, 0, 0) # Reseta cor
    pdf.ln(5)

    # --- EVIDÊNCIA ---
    if dados['foto_avaria'] and os.path.exists(dados['foto_avaria']):
        pdf.set_font('Barlow', 'B', 11)
        pdf.cell(0, 8, "Evidência Fotográfica:", ln=True)
        # Centraliza imagem (w=120) em página A4 (w=210) -> x ~ 45
        pdf.image(dados['foto_avaria'], x=45, w=120)

    # --- ASSINATURA ---
    pdf.bloco_assinatura("Técnico de Suporte")

    nome_arquivo = f"Laudo_{dados['cliente'].split()[0]}_{dados['equipamento']}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

def renderizar_formulario_equipamento():
    st.subheader("🛠️ Laudo de Avaria")
    st.caption("Geração de laudo técnico para troca ou reparo de equipamento.")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Green Park")
        equipamento = st.text_input("Equipamento", value="DVR Intelbras MHDX")
    with col2:
        serial = st.text_input("Nº Série", value="XYZ-99998888")
        data = st.date_input("Data da Análise").strftime("%d/%m/%Y")

    diagnostico = st.text_area(
        "Descrição Técnica (Detelhes do teste)", 
        height=150,
        value="Após testes na bancada, identificou-se que a placa principal não inicializa. "
              "A fonte de alimentação foi testada e está normal (12V). "
              "Componentes da placa apresentam sinais de oxidação severa."
    )
    
    conclusao = st.selectbox("Parecer Final", 
                             ["Troca Imediata (Sem conserto)", "Envio para RMA (Garantia)", "Equipamento Operacional", "Mau Uso Identificado"])

    foto = st.file_uploader("Foto do Equipamento/Etiqueta", type=['jpg', 'png', 'jpeg'])

    if st.button("Gerar Laudo Técnico", type="primary"):
        caminho_foto = ""
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
            "diagnostico": diagnostico,
            "conclusao": conclusao,
            "foto_avaria": caminho_foto
        }

        try:
            arquivo = gerar_pdf_equipamento(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Laudo gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")
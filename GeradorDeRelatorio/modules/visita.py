import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort

def gerar_pdf_visita(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE VISTORIA TÉCNICA")
    pdf.add_page()
    
    # --- CABEÇALHO DADOS ---
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Cliente / Local: {dados['cliente']}", ln=True)
    pdf.cell(0, 6, f"Data da Vistoria: {dados['data']}", ln=True)
    pdf.ln(5)

    # --- OBSERVAÇÕES (BULLET POINTS) ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. Descrição da Vistoria / Pontos Identificados", ln=True)
    
    pdf.set_font('Barlow', '', 11)
    
    # Transforma o texto do text_area em lista, separando por linha
    itens = dados['observacoes'].split('\n')
    for item in itens:
        if item.strip(): # Se a linha não for vazia
            # Adiciona um bullet point visual
            pdf.set_x(15) 
            pdf.multi_cell(0, 6, f"\u2022 {item.strip()}") # \u2022 é o código do 'bolinha'
            pdf.ln(1)
            
    pdf.ln(5)

    # --- FOTOS (GALERIA) ---
    if dados['fotos']:
        pdf.add_page() # Fotos geralmente em página nova para não quebrar
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. Registro Fotográfico (Cenário Atual)", ln=True)
        pdf.ln(5)
        
        # Lógica simples: uma foto por vez com legenda (ou duas se couber, mas vamos simplificar)
        for i, caminho_foto in enumerate(dados['fotos']):
            if os.path.exists(caminho_foto):
                # Verifica se cabe na página (imagem ~8cm altura + espaço)
                if pdf.get_y() > 200: 
                    pdf.add_page()
                
                pdf.image(caminho_foto, x=30, w=150) # Imagem larga centralizada
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 5, f"Foto {i+1}: Registro local", align='C', ln=True)
                pdf.ln(5)

    # --- ASSINATURA ---
    pdf.bloco_assinatura(dados['responsavel'])

    nome_arquivo = f"Vistoria_{dados['cliente'].split()[0]}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

def renderizar_formulario_visita():
    st.subheader("📋 Vistoria Técnica / Levantamento")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Local / Cliente", value="Residencial SQS 206")
        responsavel = st.text_input("Responsável Técnico", value="Seu Nome")
    with col2:
        data = st.date_input("Data").strftime("%d/%m/%Y")

    st.markdown("**Observações e Necessidades:** (Uma por linha)")
    obs_padrao = (
        "Fiação exposta no pilotis necessitando de proteção.\n"
        "Ponto cego identificado na entrada da garagem.\n"
        "Rack precisa de organização e limpeza.\n"
        "Sugestão: Instalar câmera Bullet na rampa de acesso."
    )
    observacoes = st.text_area("Lista de Itens", value=obs_padrao, height=150)

    fotos = st.file_uploader("Fotos do Local", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)

    if st.button("Gerar Relatório de Vistoria", type="primary"):
        lista_caminhos_fotos = []
        if fotos:
            if not os.path.exists("temp"): os.makedirs("temp")
            for arquivo in fotos:
                caminho = f"temp/visita_{arquivo.name}"
                with open(caminho, "wb") as f:
                    f.write(arquivo.getbuffer())
                lista_caminhos_fotos.append(caminho)

        dados = {
            "cliente": cliente,
            "data": data,
            "responsavel": responsavel,
            "observacoes": observacoes,
            "fotos": lista_caminhos_fotos
        }

        try:
            arquivo = gerar_pdf_visita(dados)
            st.session_state.arquivo_gerado = arquivo
            st.success("Relatório de Vistoria gerado!")
        except Exception as e:
            st.error(f"Erro: {e}")
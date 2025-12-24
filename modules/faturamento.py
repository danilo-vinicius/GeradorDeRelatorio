import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort

# --- MOTOR PDF ---
def gerar_pdf_faturamento(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE MATERIAIS E SERVIÇOS")
    
    # Capa
    pdf.gerar_capa(
        titulo_principal="Relatório para Faturamento",
        sub_titulo=f"Cliente: {dados['cliente']}\nRef: {dados['referencia']}",
        autor=dados['tecnico']
    )
    
    pdf.add_page()
    
    # Cabeçalho da Página de Itens
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data de Execução: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- TABELA DE ITENS ---
    pdf.set_font('Barlow', 'B', 11)
    pdf.set_fill_color(10, 35, 80) # Azul Brasfort
    pdf.set_text_color(255, 255, 255) # Texto Branco
    
    # Cabeçalho da Tabela
    # Larguras: Item=100, Qtd=30, Unidade=40
    pdf.cell(100, 8, "Descrição do Material / Serviço", border=1, fill=True)
    pdf.cell(30, 8, "Qtd.", border=1, fill=True, align='C')
    pdf.cell(40, 8, "Unidade", border=1, fill=True, align='C', ln=True)
    
    # Itens
    pdf.set_text_color(0, 0, 0) # Volta para preto
    pdf.set_font('Barlow', '', 10)
    
    for item in dados['lista_itens']:
        # Alterna cor de fundo para ficar bonito (Zebra striping)
        if pdf.get_y() > 240: pdf.add_page() # Quebra página se encher
        
        pdf.cell(100, 8, item['descricao'], border='B')
        pdf.cell(30, 8, str(item['qtd']), border='B', align='C')
        pdf.cell(40, 8, item['unidade'], border='B', align='C', ln=True)

    pdf.ln(10)
    
    # Observações Gerais
    if dados['observacoes']:
        pdf.set_font('Barlow', 'B', 11)
        pdf.cell(0, 8, "Observações Adicionais:", ln=True)
        pdf.set_font('Barlow', '', 10)
        pdf.multi_cell(0, 5, dados['observacoes'])
        pdf.ln(10)

    # Assinatura
    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Faturamento_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_faturamento():
    st.subheader("💰 Relatório para Faturamento")
    st.caption("Liste os materiais aplicados e serviços executados.")

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente / Local", value="Condomínio Top Life")
        referencia = st.text_input("Referência (Ex: Bloco A, Portão 2)", value="Manutenção Cancela")
    with col2:
        tecnico = st.text_input("Técnico Responsável", value="Equipe Técnica")
        data = st.date_input("Data do Serviço").strftime("%d/%m/%Y")

    st.markdown("---")
    st.write("**Lista de Itens**")
    
    # --- LISTA DINÂMICA (A mágica do Streamlit) ---
    # Inicializa a lista na sessão se não existir
    if 'itens_faturamento' not in st.session_state:
        st.session_state.itens_faturamento = []

    # Formulário para adicionar item
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1:
            novo_item = st.text_input("Item (Material ou Serviço)", placeholder="Ex: Cabo de Rede CAT6")
        with c2:
            nova_qtd = st.number_input("Qtd", min_value=0.0, step=1.0, value=1.0)
        with c3:
            nova_unid = st.selectbox("Unid.", ["un", "m", "cx", "h", "dia", "serviço"])
        with c4:
            st.write("") # Espaço para alinhar botão
            st.write("")
            if st.button("➕ Adicionar"):
                if novo_item:
                    st.session_state.itens_faturamento.append({
                        "descricao": novo_item,
                        "qtd": nova_qtd,
                        "unidade": nova_unid
                    })
                else:
                    st.warning("Digite o nome do item.")

    # Mostra a lista atual
    if st.session_state.itens_faturamento:
        st.write("Items Adicionados:")
        for i, item in enumerate(st.session_state.itens_faturamento):
            st.text(f"{i+1}. {item['descricao']} - {item['qtd']} {item['unidade']}")
        
        if st.button("Limpar Lista", type="secondary"):
            st.session_state.itens_faturamento = []
            st.rerun()
    else:
        st.info("Nenhum item adicionado ainda.")

    st.markdown("---")
    observacoes = st.text_area("Observações para o Faturamento", height=80)

    if st.button("Gerar Relatório de Faturamento", type="primary"):
        if not st.session_state.itens_faturamento:
            st.error("Adicione pelo menos um item à lista.")
        else:
            dados = {
                "cliente": cliente,
                "referencia": referencia,
                "tecnico": tecnico,
                "data": data,
                "lista_itens": st.session_state.itens_faturamento,
                "observacoes": observacoes
            }
            try:
                arquivo = gerar_pdf_faturamento(dados)
                st.session_state.arquivo_gerado = arquivo
                st.success("Relatório gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")
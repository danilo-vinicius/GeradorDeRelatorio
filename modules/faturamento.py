import streamlit as st
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

def gerar_pdf_faturamento(dados):
    # Título que vai aparecer no cabeçalho das páginas 2, 3, etc.
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE FATURAMENTO")
    
    # Gera a Capa (Página 1)
    pdf.gerar_capa(
        titulo_principal="Relatório de Faturamento",
        sub_titulo=f"Cliente: {dados['cliente']}\nReferência: {dados['referencia']}",
        autor=dados['tecnico']
    )
    
    # Adiciona Página 2 (Agora com cabeçalho automático)
    pdf.add_page()

    # Espaço antes do conteúdo
    pdf.ln(10)
    
    # --- CONTEÚDO DO RELATÓRIO ---
    
    # Introdução
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "Introdução:", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['introducao'], align='J')
    pdf.ln(5)

    # Detalhamento
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "Detalhamento do Faturamento:", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, "A seguir, apresentamos um resumo detalhado das fontes de receita que compõem o faturamento total.", align='J')
    pdf.ln(5)

    # --- TABELA DE ITENS ---
    # Cabeçalho da Tabela
    pdf.set_fill_color(10, 35, 80) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Barlow', 'B', 10)
    
    pdf.cell(100, 8, "Descrição do Material / Serviço", border=1, fill=True)
    pdf.cell(20, 8, "Qtd.", border=1, fill=True, align='C')
    pdf.cell(35, 8, "Valor Unit.", border=1, fill=True, align='C')
    pdf.cell(35, 8, "Preço Total", border=1, fill=True, align='C', ln=True)
    
    # Itens
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Barlow', '', 10)
    
    total_geral = 0.0

    for i, item in enumerate(dados['lista_itens']):
        fill = True if i % 2 == 0 else False
        pdf.set_fill_color(245, 245, 245)

        qtd = item['qtd']
        valor_unit = item['valor']
        total_item = qtd * valor_unit
        total_geral += total_item

        str_unit = f"R$ {valor_unit:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        str_total = f"R$ {total_item:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        pdf.cell(100, 8, item['descricao'], border='LB', fill=fill)
        pdf.cell(20, 8, str(qtd), border='B', align='C', fill=fill)
        pdf.cell(35, 8, str_unit, border='B', align='C', fill=fill)
        pdf.cell(35, 8, str_total, border='RB', align='C', fill=fill, ln=True)

    # Total Geral
    pdf.ln(2)
    pdf.set_font('Barlow', 'B', 12)
    str_total_geral = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    # Alinhado à direita para ficar bonito
    pdf.cell(155, 10, "Total Geral:", border=0, align='R')
    pdf.set_fill_color(200, 230, 200) # Verde suave
    pdf.cell(35, 10, str_total_geral, border=1, align='C', fill=True, ln=True)
    pdf.ln(10)
    
    # Observações
    if dados['observacoes']:
        pdf.set_font('Barlow', 'B', 11)
        pdf.cell(0, 8, "Observações Adicionais:", ln=True)
        pdf.set_font('Barlow', '', 10)
        pdf.multi_cell(0, 5, dados['observacoes'])
        pdf.ln(10)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Faturamento_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_formulario_faturamento():
    st.subheader("💰 Relatório de Faturamento")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Condomínio Top Life")
        referencia = st.text_input("Referência (Local/Bloco)", value="Manutenção Geral")
    with col2:
        tecnico = st.text_input("Responsável Técnico", value="Luciano Pereira do Nascimento")
        data = st.date_input("Data do Relatório").strftime("%d/%m/%Y")

    st.markdown("---")
    
    texto_padrao = "O presente relatório tem como objetivo apresentar a prestação de contas referente ao faturamento ocorrido no período especificado. Esta prestação de contas visa fornecer uma visão clara e transparente das receitas obtidas."
    introducao = st.text_area("Introdução:", value=texto_padrao, height=70)

    st.markdown("---")
    st.write("### 📝 Itens do Faturamento")
    
    if 'itens_faturamento' not in st.session_state:
        st.session_state.itens_faturamento = []

    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
        with c1: novo_item = st.text_input("Descrição", placeholder="Ex: Cabo UTP")
        with c2: nova_qtd = st.number_input("Qtd", min_value=0.0, step=1.0, value=1.0)
        with c3: novo_valor = st.number_input("Valor (R$)", min_value=0.0, step=0.50)
        with c4:
            st.write("") 
            st.write("")
            if st.button("➕ Adicionar"):
                if novo_item:
                    st.session_state.itens_faturamento.append({
                        "descricao": novo_item, "qtd": nova_qtd, "valor": novo_valor
                    })
                    st.rerun()

    if st.session_state.itens_faturamento:
        st.table(st.session_state.itens_faturamento)
        if st.button("Limpar Lista"):
            st.session_state.itens_faturamento = []
            st.rerun()

    st.markdown("---")
    observacoes = st.text_area("Observações:", height=60)

    if st.button("Gerar Relatório", type="primary"):
        if not st.session_state.itens_faturamento:
            st.error("Adicione itens!")
        else:
            dados = {
                "cliente": cliente, "referencia": referencia, "tecnico": tecnico,
                "data": data, "introducao": introducao,
                "lista_itens": st.session_state.itens_faturamento, "observacoes": observacoes
            }
            try:
                arquivo = gerar_pdf_faturamento(dados)
                st.session_state['arquivo_pronto'] = arquivo
                st.success("Sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")

    if 'arquivo_pronto' in st.session_state:
        with open(st.session_state['arquivo_pronto'], "rb") as f:
            st.download_button("📥 Baixar PDF", f, file_name="Relatorio.pdf")
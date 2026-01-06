import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

# --- MOTOR PDF ---
def gerar_pdf_faturamento(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO DE FATURAMENTO")
    
    # --- SEM CAPA (Conforme sua alteração) ---
    # pdf.gerar_capa(...) <--- Comentado/Removido
    
    pdf.add_page()
    
    # Cabeçalho da Página
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data: {dados['data']}", ln=True)
    pdf.ln(10)

    # Introdução
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "Introdução:", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['introducao'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "Detalhamento do Faturamento:", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, "A seguir, apresentamos um resumo detalhado das fontes de receita que compõem o faturamento total.", align='J')
    pdf.ln(5)

    # Tabela
    pdf.set_font('Barlow', 'B', 10)
    pdf.set_fill_color(10, 35, 80) 
    pdf.set_text_color(255, 255, 255) 
    pdf.cell(100, 8, "Descrição do Material / Serviço", border=1, fill=True)
    pdf.cell(20, 8, "Qtd.", border=1, fill=True, align='C')
    pdf.cell(35, 8, "Valor Unit.", border=1, fill=True, align='C')
    pdf.cell(35, 8, "Preço Total", border=1, fill=True, align='C', ln=True)
    
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

    pdf.ln(2)
    pdf.set_font('Barlow', 'B', 12)
    str_total_geral = f"R$ {total_geral:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    pdf.cell(155, 10, "Total Geral:", border=0, align='R')
    pdf.set_fill_color(200, 230, 200)
    pdf.cell(35, 10, str_total_geral, border=1, align='C', fill=True, ln=True)
    pdf.ln(10)
    
    if dados['observacoes']:
        pdf.set_font('Barlow', 'B', 11)
        pdf.cell(0, 8, "Observações Adicionais:", ln=True)
        pdf.set_font('Barlow', '', 10)
        pdf.multi_cell(0, 5, dados['observacoes'])
        pdf.ln(10)

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Faturamento_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE SPLIT ---
def renderizar_formulario_faturamento():
    st.subheader("💰 Relatório de Faturamento")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO ===
    with col_form:
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio Top Life")
        referencia = c1.text_input("Referência", value="Manutenção Geral")
        tecnico = c2.text_input("Responsável Técnico", value="Luciano Pereira")
        data = c2.date_input("Data do Relatório").strftime("%d/%m/%Y")

        st.markdown("---")
        
        texto_padrao = "O presente relatório tem como objetivo apresentar a prestação de contas referente ao faturamento ocorrido no período especificado. Esta prestação de contas visa fornecer uma visão clara e transparente das receitas obtidas."
        introducao = st.text_area("Introdução:", value=texto_padrao, height=70)

        st.markdown("---")
        st.write("### 📝 Itens do Faturamento")
        
        if 'itens_faturamento' not in st.session_state: st.session_state.itens_faturamento = []

        with st.container(border=True):
            ci1, ci2, ci3, ci4 = st.columns([3, 1, 1, 1])
            novo_item = ci1.text_input("Descrição", placeholder="Ex: Cabo UTP", key="novo_item")
            nova_qtd = ci2.number_input("Qtd", min_value=0.0, step=1.0, value=1.0, key="novo_qtd")
            novo_valor = ci3.number_input("Valor (R$)", min_value=0.0, step=0.50, key="novo_valor")
            ci4.write("")
            ci4.write("")
            if ci4.button("➕"):
                if novo_item:
                    st.session_state.itens_faturamento.append({"descricao": novo_item, "qtd": nova_qtd, "valor": novo_valor})
                    st.rerun()

        if st.session_state.itens_faturamento:
            lista_visual = []
            total_preview = 0
            for item in st.session_state.itens_faturamento:
                total = item['qtd'] * item['valor']
                total_preview += total
                lista_visual.append({
                    "Descrição": item['descricao'], "Qtd": item['qtd'],
                    "Unitário": f"R$ {item['valor']:.2f}", "Total": f"R$ {total:.2f}"
                })
            
            st.table(lista_visual)
            st.info(f"**Total Geral: R$ {total_preview:,.2f}**")
            
            if st.button("Limpar Lista"):
                st.session_state.itens_faturamento = []
                st.rerun()

        st.markdown("---")
        st.write("**Observações**")
        if "txt_obs_fat" not in st.session_state: st.session_state.txt_obs_fat = ""
        rascunho_obs = st.text_area("Rascunho:", height=60, key="ras_obs")
        if st.button("IA: Melhorar Texto", key="btn_ia_obs"):
            st.session_state.txt_obs_fat = melhorar_texto_com_ia(rascunho_obs, "Observação Financeira")
            st.rerun()
        observacoes_final = st.text_area("Final:", value=st.session_state.txt_obs_fat, height=80, key="fin_obs")

    # === LADO DIREITO ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            if not st.session_state.itens_faturamento:
                st.error("Adicione itens à lista.")
            else:
                dados = {
                    "cliente": cliente, "referencia": referencia, "tecnico": tecnico,
                    "data": data, "introducao": introducao,
                    "lista_itens": st.session_state.itens_faturamento, "observacoes": observacoes_final
                }
                try:
                    path = gerar_pdf_faturamento(dados)
                    st.session_state['pdf_fat_view'] = path
                    st.toast("Atualizado!", icon="✅")
                except Exception as e:
                    st.error(f"Erro: {e}")

        if 'pdf_fat_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_fat_view'])
            with open(st.session_state['pdf_fat_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Faturamento.pdf", "application/pdf", use_container_width=True)
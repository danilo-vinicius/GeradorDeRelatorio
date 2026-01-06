import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

def gerar_pdf_parecer(dados):
    pdf = RelatorioBrasfort(titulo="PARECER TÉCNICO DE ENGENHARIA")
    pdf.gerar_capa(titulo_principal="Parecer Técnico", sub_titulo=f"Assunto: {dados['assunto']}\nCliente: {dados['cliente']}", autor=dados['responsavel'])
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Referência: {dados['assunto']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data da Emissão: {dados['data']}", ln=True)
    pdf.ln(10)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "1. OBJETIVO DA ANÁLISE", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['historico'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. METODOLOGIA", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['metodologia'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "3. ANÁLISE TÉCNICA E CONSTATAÇÕES", ln=True)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['analise'], align='J')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "4. CONCLUSÃO", ln=True)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    pdf.bloco_assinatura(dados['responsavel'])
    
    nome_arquivo = f"Parecer_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

def renderizar_formulario_parecer():
    st.subheader("⚖️ Parecer Técnico")
    col_form, col_view = st.columns([0.55, 0.45])

    with col_form:
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio Solar")
        assunto = c1.text_input("Assunto", value="Queima de Central")
        responsavel = c2.text_input("Responsável", value="Eng. Técnico")
        data = c2.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")
        
        st.write("### 1. Histórico")
        if "txt_par_hist" not in st.session_state: st.session_state.txt_par_hist = ""
        rascunho_hist = st.text_area("O que aconteceu?", height=70, key="ras_hist")
        if st.button("IA: Formalizar Histórico", key="btn_hist"):
            st.session_state.txt_par_hist = melhorar_texto_com_ia(rascunho_hist, "Histórico")
            st.rerun()
        hist_final = st.text_area("Final:", value=st.session_state.txt_par_hist, height=100, key="fin_hist")

        st.write("### 2. Metodologia")
        metodologia = st.text_area("Como testou?", value="Inspeção visual e medição de tensões.", height=70, key="metodo")

        st.write("### 3. Análise")
        if "txt_par_ana" not in st.session_state: st.session_state.txt_par_ana = ""
        rascunho_ana = st.text_area("Achados técnicos:", height=100, key="ras_ana")
        if st.button("IA: Formalizar Análise", key="btn_ana"):
            st.session_state.txt_par_ana = melhorar_texto_com_ia(rascunho_ana, "Análise Técnica")
            st.rerun()
        analise_final = st.text_area("Final:", value=st.session_state.txt_par_ana, height=150, key="fin_ana")

        st.write("### 4. Conclusão")
        if "txt_par_conc" not in st.session_state: st.session_state.txt_par_conc = ""
        rascunho_conc = st.text_area("Veredito:", height=70, key="ras_conc")
        if st.button("IA: Concluir", key="btn_conc"):
            st.session_state.txt_par_conc = melhorar_texto_com_ia(rascunho_conc, "Conclusão Parecer")
            st.rerun()
        conclusao_final = st.text_area("Final:", value=st.session_state.txt_par_conc, height=100, key="fin_conc")

    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            dados = {
                "cliente": cliente, "assunto": assunto, "responsavel": responsavel, "data": data,
                "historico": hist_final, "metodologia": metodologia, "analise": analise_final, "conclusao": conclusao_final
            }
            try:
                path = gerar_pdf_parecer(dados)
                st.session_state['pdf_parecer_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_parecer_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_parecer_view'])
            with open(st.session_state['pdf_parecer_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Parecer.pdf", "application/pdf", use_container_width=True)
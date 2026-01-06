import streamlit as st
import pandas as pd
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

# --- MOTOR PDF (MANTIDO IGUAL) ---
def gerar_pdf_cronograma(dados):
    pdf = RelatorioBrasfort(titulo="CRONOGRAMA TÉCNICO")
    
    subtitulo_capa = f"Cliente: {dados['cliente']}\nReferência: {dados['referencia']}"
    titulo_principal = "CRONOGRAMA DE IMPLEMENTAÇÃO / PROJETO" if dados['tipo'] == 'fases' else "CRONOGRAMA DE VISITAS E ACOMPANHAMENTO"

    pdf.gerar_capa(titulo_principal=titulo_principal, sub_titulo=subtitulo_capa, autor=dados['tecnico'])
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data Base: {dados['data']}", ln=True)
    pdf.ln(10)

    if dados['introducao']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. OBJETIVO E METODOLOGIA", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['introducao'], align='J')
        pdf.ln(10)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. DETALHAMENTO DO CRONOGRAMA", ln=True)
    pdf.ln(2)

    if dados['tipo'] == 'tabela':
        if not dados['df_tabela'].empty:
            pdf.set_font('Barlow', 'B', 10)
            pdf.set_fill_color(10, 35, 80)
            pdf.set_text_color(255, 255, 255)
            cols = [("Local / Atividade", 80), ("Data Prevista", 35), ("Status", 35), ("Observação", 40)]
            for nome, larg in cols:
                pdf.cell(larg, 8, nome, 1, 0, 'C', True)
            pdf.ln()
            
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Barlow', '', 10)
            
            for index, row in dados['df_tabela'].iterrows():
                fill = True if index % 2 == 0 else False
                pdf.set_fill_color(240, 240, 240)
                local = str(row.get("Local / Atividade", ""))
                data = str(row.get("Data", ""))
                status = str(row.get("Status", ""))
                obs = str(row.get("Obs", ""))

                pdf.set_text_color(0,0,0)
                if "Realizada" in status or "Concluído" in status: pdf.set_text_color(0, 100, 0)
                elif "Pendente" in status or "Prevista" in status: pdf.set_text_color(200, 100, 0)

                pdf.cell(80, 8, local, 1, 0, 'L', fill)
                pdf.set_text_color(0,0,0)
                pdf.cell(35, 8, data, 1, 0, 'C', fill)
                
                if "Realizada" in status or "Concluído" in status: pdf.set_text_color(0, 100, 0)
                elif "Pendente" in status or "Prevista" in status: pdf.set_text_color(200, 100, 0)
                pdf.cell(35, 8, status, 1, 0, 'C', fill)
                
                pdf.set_text_color(0,0,0)
                pdf.cell(40, 8, obs, 1, 1, 'L', fill)
    else:
        for fase in dados['lista_fases']:
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font('Barlow', 'B', 11)
            pdf.cell(0, 8, f" {fase['titulo'].upper()}", ln=True, fill=True, border='L')
            pdf.set_font('Barlow', '', 11)
            pdf.multi_cell(0, 6, fase['conteudo'], align='J')
            pdf.ln(5)

    pdf.ln(5)
    if dados['conclusao']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. CONSIDERAÇÕES FINAIS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['conclusao'], align='J')

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Cronograma_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE SPLIT ---
def renderizar_cronograma():
    st.subheader("📅 Gerador de Cronogramas")
    
    col_form, col_view = st.columns([0.55, 0.45])

    # === LADO ESQUERDO ===
    with col_form:
        modo = st.radio("Tipo:", ["Tabela de Acompanhamento", "Projeto por Fases"], horizontal=True)
        tipo = "tabela" if "Tabela" in modo else "fases"

        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Grupo CIPLAN")
        referencia = c1.text_input("Referência", value="Modernização")
        tecnico = c2.text_input("Responsável", value="Luciano Pereira")
        data = c2.date_input("Data Base").strftime("%d/%m/%Y")

        st.markdown("---")
        st.write("**1. Introdução**")
        if "txt_crono_intro" not in st.session_state: st.session_state.txt_crono_intro = ""
        rascunho_intro = st.text_area("Objetivo:", height=70, key="ras_intro")
        if st.button("IA: Formalizar", key="btn_intro"):
            st.session_state.txt_crono_intro = melhorar_texto_com_ia(rascunho_intro, "Objetivo Cronograma")
            st.rerun()
        intro_final = st.text_area("Final:", value=st.session_state.txt_crono_intro, height=100, key="fin_intro")

        st.markdown("---")
        st.write("**2. Estrutura**")

        df_final = pd.DataFrame()
        lista_fases_final = []

        if tipo == "tabela":
            if "df_cronograma" not in st.session_state:
                st.session_state.df_cronograma = pd.DataFrame([{"Local / Atividade": "Visita Inicial", "Data": "10/10/2025", "Status": "Realizada", "Obs": "OK"}])
            
            df_final = st.data_editor(st.session_state.df_cronograma, num_rows="dynamic", use_container_width=True, 
                                      column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Agendada", "Realizada", "Pendente"], required=True)})
        else:
            if "fases_cronograma" not in st.session_state: st.session_state.fases_cronograma = []
            c_add1, c_add2 = st.columns([3, 1])
            nova_fase = c_add1.text_input("Nova Fase", placeholder="Fase 1")
            if c_add2.button("➕"):
                if nova_fase:
                    st.session_state.fases_cronograma.append({"titulo": nova_fase, "conteudo": ""})
                    st.rerun()

            for i, fase in enumerate(st.session_state.fases_cronograma):
                with st.container(border=True):
                    c_head1, c_head2 = st.columns([0.9, 0.1])
                    c_head1.write(f"**{fase['titulo']}**")
                    if c_head2.button("X", key=f"del_fase_{i}"):
                        st.session_state.fases_cronograma.pop(i)
                        st.rerun()
                    
                    txt_fase = st.text_area(f"Atividades", value=fase['conteudo'], height=100, key=f"txt_fase_{i}")
                    if st.button(f"IA: Formatar Datas", key=f"ia_fase_{i}"):
                        novo_texto = melhorar_texto_com_ia(f"Formate cronologicamente: {txt_fase}", "Lista")
                        st.session_state.fases_cronograma[i]['conteudo'] = novo_texto
                        st.rerun()
                    
                    if txt_fase != fase['conteudo']:
                        st.session_state.fases_cronograma[i]['conteudo'] = txt_fase
            lista_fases_final = st.session_state.fases_cronograma

        st.markdown("---")
        st.write("**3. Conclusão**")
        if "txt_crono_conc" not in st.session_state: st.session_state.txt_crono_conc = ""
        rascunho_conc = st.text_area("Considerações:", height=70, key="ras_conc")
        if st.button("IA: Concluir", key="btn_conc"):
            st.session_state.txt_crono_conc = melhorar_texto_com_ia(rascunho_conc, "Conclusão")
            st.rerun()
        conc_final = st.text_area("Final:", value=st.session_state.txt_crono_conc, height=80, key="fin_conc")

    # === LADO DIREITO ===
    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            dados = {
                "tipo": tipo, "cliente": cliente, "referencia": referencia, "tecnico": tecnico, "data": data,
                "introducao": intro_final, "df_tabela": df_final, "lista_fases": lista_fases_final, "conclusao": conc_final
            }
            try:
                path = gerar_pdf_cronograma(dados)
                st.session_state['pdf_crono_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_crono_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_crono_view'])
            with open(st.session_state['pdf_crono_view'], "rb") as f:
                st.download_button("📥 BAIXAR PDF FINAL", f, "Cronograma.pdf", "application/pdf", use_container_width=True)
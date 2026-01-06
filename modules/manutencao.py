import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela # <--- Importe a nova função

# --- MOTOR PDF (MANTIDO IGUAL) ---
def gerar_pdf_manutencao(dados):
    pdf = RelatorioBrasfort(titulo="RELATÓRIO TÉCNICO")
    
    if dados['tipo'] == "Corretiva":
        titulo_capa = "RELATÓRIO DE MANUTENÇÃO CORRETIVA"
    elif dados['tipo'] == "Preventiva":
        titulo_capa = "RELATÓRIO DE MANUTENÇÃO PREVENTIVA"
    else:
        titulo_capa = "RELATÓRIO DE VERIFICAÇÃO TÉCNICA" 
    
    pdf.gerar_capa(
        titulo_principal=titulo_capa,
        sub_titulo=f"Cliente: {dados['cliente']}\nLocal: {dados['local']}\nSistema: {dados['sistema']}",
        autor=dados['tecnico']
    )
    
    pdf.add_page()
    pdf.ln(20)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Local: {dados['local']} - Data: {dados['data']}", ln=True)
    pdf.ln(10)

    if dados['tipo'] == "Corretiva":
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. DESCRIÇÃO DA OCORRÊNCIA / SOLICITAÇÃO", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_ocorrencia'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "2. ATIVIDADES REALIZADAS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_atividades'], align='J')
        pdf.ln(5)

        if dados['pecas']:
            pdf.set_font('Barlow', 'B', 12)
            pdf.cell(0, 8, "3. PEÇAS SUBSTITUÍDAS / INSTALADAS", ln=True)
            pdf.set_font('Barlow', '', 11)
            pdf.multi_cell(0, 6, dados['pecas'], align='J')
            pdf.ln(5)

    else:
        titulo_1 = "1. OBJETIVO / O QUE FOI INSPECCIONADO" if dados['tipo'] == "Verificação" else "1. VERIFICAÇÃO GERAL E INSPEÇÃO"
        titulo_2 = "2. PROCEDIMENTOS REALIZADOS E RESULTADOS" if dados['tipo'] == "Verificação" else "2. SITUAÇÕES IDENTIFICADAS / AJUSTES"
        titulo_3 = "3. STATUS DOS EQUIPAMENTOS"
        
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_1, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_verificacao'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_2, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_situacoes'], align='J')
        pdf.ln(5)

        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, titulo_3, ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['texto_equipamentos'], align='J')
        pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    titulo_conclusao = "RESSALVAS E RECOMENDAÇÕES" if dados['tipo'] == "Verificação" else "CONCLUSÃO / STATUS FINAL"
    pdf.cell(0, 8, titulo_conclusao, ln=True)
    
    pdf.set_font('Barlow', 'B', 11)
    if "Operacional" in dados['status'] or "Operante" in dados['status']:
        pdf.set_text_color(0, 150, 0)
    else:
        pdf.set_text_color(200, 100, 0)
    
    pdf.cell(0, 8, f"Status: {dados['status']}", ln=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['conclusao'], align='J')
    pdf.ln(10)

    if dados['lista_fotos']:
        if pdf.get_y() > 200: pdf.add_page()
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "REGISTRO FOTOGRÁFICO / EVIDÊNCIAS", ln=True)
        pdf.ln(5)
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            legenda = item['legenda']
            if os.path.exists(caminho):
                if pdf.get_y() + 90 > 280: pdf.add_page()
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"{legenda}", align='C', ln=True)
                pdf.ln(8)

    pdf.bloco_assinatura(dados['tecnico'])
    prefixo = "Verificacao" if dados['tipo'] == "Verificação" else "Manutencao"
    nome_arquivo = f"{prefixo}_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

# --- INTERFACE ---
def renderizar_formulario_manutencao():
    st.set_page_config(layout="wide") # Garante tela cheia para caber tudo
    st.subheader("🛠️ Relatório Técnico")

    # --- DIVISÃO DA TELA (LAYOUT) ---
    col_form, col_preview = st.columns([0.55, 0.45]) # 55% Form, 45% Preview

    # === LADO ESQUERDO: FORMULÁRIO ===
    with col_form:
        tipo_manutencao = st.radio("Tipo:", ["Corretiva (Reparo)", "Preventiva (Rotina)", "Verificação Técnica"], horizontal=True)
        if "Corretiva" in tipo_manutencao: modo = "Corretiva"
        elif "Preventiva" in tipo_manutencao: modo = "Preventiva"
        else: modo = "Verificação"

        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Condomínio Jardim das Cerejeiras")
        local = c1.text_input("Local/Bloco", value="Garagem")
        tecnico = c2.text_input("Técnico", value="Seu Nome")
        sistema = c2.text_input("Sistema", value="LPR e Semáforos")
        data = st.date_input("Data").strftime("%d/%m/%Y")

        st.markdown("---")

        # Variáveis de texto
        texto_ocorrencia_final = ""
        texto_atividades_final = ""
        texto_pecas = ""
        texto_verificacao_final = ""
        texto_situacoes_final = ""
        texto_equipamentos_final = ""

        if modo == "Corretiva":
            if "txt_man_oco" not in st.session_state: st.session_state.txt_man_oco = ""
            rascunho_oco = st.text_area("1. Qual foi o problema?", height=60, key="rascunho_oco")
            if st.button("IA: Formalizar Problema", key="btn_oco"):
                st.session_state.txt_man_oco = melhorar_texto_com_ia(rascunho_oco, "Ocorrência")
                st.rerun() # Recarrega para atualizar preview
            texto_ocorrencia_final = st.text_area("Final:", value=st.session_state.txt_man_oco, height=80, key="fin_oco")

            if "txt_man_ativ" not in st.session_state: st.session_state.txt_man_ativ = ""
            rascunho_ativ = st.text_area("2. O que foi feito?", height=80, key="rascunho_ativ")
            if st.button("IA: Formalizar Ação", key="btn_ativ"):
                st.session_state.txt_man_ativ = melhorar_texto_com_ia(rascunho_ativ, "Atividades")
                st.rerun()
            texto_atividades_final = st.text_area("Final:", value=st.session_state.txt_man_ativ, height=120, key="fin_ativ")
            texto_pecas = st.text_input("3. Peças Utilizadas", key="pecas")

        else: # Preventiva/Verificação
            label_1 = "1. Objetivo / Inspecionado" if modo == "Verificação" else "1. Itens Inspecionados"
            if "txt_prev_ver" not in st.session_state: st.session_state.txt_prev_ver = ""
            rascunho_ver = st.text_area(label_1, height=60, key="ras_ver")
            if st.button("IA: Formalizar", key="btn_ver"):
                st.session_state.txt_prev_ver = melhorar_texto_com_ia(rascunho_ver, "Objetivo")
                st.rerun()
            texto_verificacao_final = st.text_area("Final:", value=st.session_state.txt_prev_ver, height=80, key="fin_ver")

            label_2 = "2. Procedimentos/Resultados" if modo == "Verificação" else "2. Ajustes Realizados"
            if "txt_prev_sit" not in st.session_state: st.session_state.txt_prev_sit = ""
            rascunho_sit = st.text_area(label_2, height=80, key="ras_sit")
            if st.button("IA: Formalizar", key="btn_sit"):
                st.session_state.txt_prev_sit = melhorar_texto_com_ia(rascunho_sit, "Procedimentos")
                st.rerun()
            texto_situacoes_final = st.text_area("Final:", value=st.session_state.txt_prev_sit, height=100, key="fin_sit")

            label_3 = "3. Status Equipamentos"
            texto_equipamentos_final = st.text_area(label_3, value="Sistema operante.", height=80, key="fin_equip")

        st.markdown("---")
        status_final = st.selectbox("Status Geral:", ["Sistema Operante", "Operante com Ressalvas", "Inoperante"])
        
        if "txt_man_conc" not in st.session_state: st.session_state.txt_man_conc = ""
        rascunho_conc = st.text_area("Recomendação/Conclusão:", height=60, key="ras_conc")
        if st.button("IA: Concluir", key="btn_conc"):
            st.session_state.txt_man_conc = melhorar_texto_com_ia(rascunho_conc, "Conclusão")
            st.rerun()
        conclusao_final = st.text_area("Final:", value=st.session_state.txt_man_conc, height=80, key="fin_conc")

        upload_fotos = st.file_uploader("Evidências", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
        legendas = {}
        if upload_fotos:
            for f in upload_fotos:
                legendas[f.name] = st.text_input(f"Legenda {f.name}", value="Evidência", key=f"leg_{f.name}")

    # === LADO DIREITO: PREVIEW DO PDF ===
    with col_preview:
        st.write("### 👁️ Visualização em Tempo Real")
        
        # Botão Grande de Atualizar
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            # 1. Processa Fotos
            lista_fotos = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for f in upload_fotos:
                    path = f"temp/view_{f.name}"
                    with open(path, "wb") as file: file.write(f.getbuffer())
                    lista_fotos.append({"caminho": path, "legenda": legendas[f.name]})

            # 2. Monta Dados
            dados = {
                "tipo": modo,
                "cliente": cliente, "local": local, "tecnico": tecnico, "sistema": sistema, "data": data,
                "texto_ocorrencia": texto_ocorrencia_final,
                "texto_atividades": texto_atividades_final,
                "pecas": texto_pecas,
                "texto_verificacao": texto_verificacao_final,
                "texto_situacoes": texto_situacoes_final,
                "texto_equipamentos": texto_equipamentos_final,
                "status": status_final,
                "conclusao": conclusao_final,
                "lista_fotos": lista_fotos
            }

            # 3. Gera PDF Temporário
            try:
                caminho_pdf = gerar_pdf_manutencao(dados)
                st.session_state['pdf_preview_path'] = caminho_pdf
                st.toast("Visualização atualizada!", icon="✅")
            except Exception as e:
                st.error(f"Erro ao gerar preview: {e}")

        # Mostra o PDF se ele existir
        if 'pdf_preview_path' in st.session_state:
            st.markdown("---")
            exibir_pdf_na_tela(st.session_state['pdf_preview_path'])
            
            # Botão de Download Final
            with open(st.session_state['pdf_preview_path'], "rb") as f:
                st.download_button(
                    label="📥 BAIXAR PDF FINAL",
                    data=f,
                    file_name="Relatorio_Manutencao.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        else:
            st.info("Preencha os dados e clique em 'Atualizar Visualização' para ver o PDF aqui.")
import streamlit as st
import os
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia
from utils.visualizador import exibir_pdf_na_tela

def gerar_pdf_os(dados):
    pdf = RelatorioBrasfort(titulo="ORDEM DE SERVIÇO")
    pdf.add_page()
    pdf.ln(5) # Espaço do topo

    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(200, 200, 200)
    
    pdf.set_font('Barlow', 'B', 14)
    pdf.cell(0, 10, f"ORDEM DE SERVIÇO Nº {dados['numero_os']}", ln=True, align='R')
    pdf.ln(2)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "DADOS DO CLIENTE", ln=True, fill=True)
    pdf.cell(15, 6, "Cliente:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, dados['cliente'], 0, 1)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(15, 6, "Local:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.multi_cell(0, 6, dados['local'])
    pdf.ln(4)

    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "DADOS TÉCNICOS DA O.S.", ln=True, fill=True)
    pdf.cell(25, 6, "Classificação:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(60, 6, dados['classificacao'], 0, 0)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(15, 6, "Tipo:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, dados['tipo_servico'], 0, 1)
    
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(25, 6, "Equipamento:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(60, 6, dados['equipamento'], 0, 0)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(30, 6, "Data Atendimento:", 0, 0)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(0, 6, f"{dados['data']} - {dados['hora_inicio']} às {dados['hora_fim']}", 0, 1)
    
    pdf.ln(2)
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(0, 6, "Necessidade / Solicitação:", ln=True)
    pdf.set_font('Barlow', '', 10)
    pdf.multi_cell(0, 6, dados['necessidade'], border='L')
    pdf.ln(5)

    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "HISTÓRICO DE AÇÕES REALIZADAS", ln=True, fill=True)
    pdf.ln(2)
    pdf.set_font('Barlow', '', 11)
    pdf.multi_cell(0, 6, dados['relato_tecnico'], border=1, align='J')
    pdf.ln(5)

    if dados['observacoes']:
        pdf.set_font('Barlow', 'B', 10)
        pdf.cell(0, 6, "Observações / Pendências:", ln=True)
        pdf.set_font('Barlow', '', 10)
        pdf.multi_cell(0, 6, dados['observacoes'], border='L')
        pdf.ln(5)

    if dados['lista_fotos']:
        pdf.ln(5)
        pdf.set_font('Barlow', 'B', 10)
        pdf.cell(0, 6, "ANEXOS / EVIDÊNCIAS", ln=True, fill=True)
        pdf.ln(5)
        for i, item in enumerate(dados['lista_fotos']):
            caminho = item['caminho']
            if os.path.exists(caminho):
                if pdf.get_y() + 90 > 280: pdf.add_page()
                x_pos = (210 - 120) / 2
                pdf.image(caminho, x=x_pos, w=120)
                pdf.ln(2)
                pdf.set_font('Barlow', 'I', 9)
                pdf.cell(0, 6, f"Anexo {i+1}", align='C', ln=True)
                pdf.ln(8)

    if pdf.get_y() > 240: pdf.add_page()
    pdf.set_y(-50)
    pdf.set_font('Barlow', '', 10)
    pdf.cell(90, 6, "___________________________________", 0, 0, 'C')
    pdf.cell(10, 6, "", 0, 0)
    pdf.cell(90, 6, "___________________________________", 0, 1, 'C')
    pdf.set_font('Barlow', 'B', 10)
    pdf.cell(90, 5, dados['tecnico'], 0, 0, 'C')
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, "Responsável Cliente", 0, 1, 'C')
    pdf.set_font('Barlow', '', 9)
    pdf.cell(90, 5, "Técnico Brasfort", 0, 0, 'C')
    pdf.cell(10, 5, "", 0, 0)
    pdf.cell(90, 5, "Aceite dos Serviços", 0, 1, 'C')

    nome_arquivo = f"OS_{dados['numero_os']}_{dados['cliente'].split()[0]}.pdf"
    path_final = os.path.join("temp", nome_arquivo)
    if not os.path.exists("temp"): os.makedirs("temp")
    pdf.output(path_final)
    return path_final

def renderizar_formulario_os():
    st.subheader("🛠️ Emissor de Ordem de Serviço (Backup)")
    col_form, col_view = st.columns([0.55, 0.45])

    with col_form:
        c1, c2, c3 = st.columns([1, 2, 1])
        num_os = c1.text_input("Nº da O.S.", value="1850")
        classif = c2.selectbox("Classe:", ["SEGURANÇA ELETRÔNICA", "INFRAESTRUTURA", "TI"])
        tipo = c3.selectbox("Tipo:", ["Man. Corretiva", "Man. Preventiva", "Instalação", "Verificação"])

        c1, c2 = st.columns(2)
        cliente = c1.text_input("Cliente", value="Brasfort Adm")
        local = c1.text_input("Local", value="Sede - SIA")
        equip = c2.text_input("Equipamento", value="CFTV Geral")
        tecnico = c2.text_input("Técnico", value="Luciano Pereira")

        cd, ch1, ch2 = st.columns(3)
        data = cd.date_input("Data").strftime("%d/%m/%Y")
        hora_ini = ch1.text_input("Início", value="08:00")
        hora_fim = ch2.text_input("Fim", value="10:00")

        st.markdown("---")
        st.write("**1. Necessidade**")
        if "txt_os_nec" not in st.session_state: st.session_state.txt_os_nec = ""
        rascunho_nec = st.text_area("O que pediram?", height=60, key="ras_nec")
        if st.button("IA: Formalizar", key="btn_nec"):
            st.session_state.txt_os_nec = melhorar_texto_com_ia(rascunho_nec, "Solicitação")
            st.rerun()
        nec_final = st.text_area("Final:", value=st.session_state.txt_os_nec, height=70, key="fin_nec")

        st.write("**2. Relato Técnico**")
        if "txt_os_rel" not in st.session_state: st.session_state.txt_os_rel = ""
        rascunho_rel = st.text_area("O que foi feito?", height=100, key="ras_rel")
        if st.button("IA: Formalizar Relato", key="btn_rel"):
            st.session_state.txt_os_rel = melhorar_texto_com_ia(rascunho_rel, "Execução")
            st.rerun()
        rel_final = st.text_area("Final:", value=st.session_state.txt_os_rel, height=150, key="fin_rel")

        obs = st.text_input("Observações:", placeholder="Pendências...", key="obs")
        
        st.markdown("---")
        upload_fotos = st.file_uploader("Evidências", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

    with col_view:
        st.write("### 👁️ Visualização")
        if st.button("🔄 ATUALIZAR VISUALIZAÇÃO", type="primary", use_container_width=True):
            lista_fotos = []
            if upload_fotos:
                if not os.path.exists("temp"): os.makedirs("temp")
                for f in upload_fotos:
                    path = f"temp/view_os_{f.name}"
                    with open(path, "wb") as file: file.write(f.getbuffer())
                    lista_fotos.append({"caminho": path, "legenda": ""})

            dados = {
                "numero_os": num_os, "classificacao": classif, "tipo_servico": tipo,
                "cliente": cliente, "local": local, "equipamento": equip, "tecnico": tecnico,
                "data": data, "hora_inicio": hora_ini, "hora_fim": hora_fim,
                "necessidade": nec_final, "relato_tecnico": rel_final,
                "observacoes": obs, "lista_fotos": lista_fotos
            }
            try:
                path = gerar_pdf_os(dados)
                st.session_state['pdf_os_view'] = path
                st.toast("Atualizado!", icon="✅")
            except Exception as e:
                st.error(f"Erro: {e}")

        if 'pdf_os_view' in st.session_state:
            exibir_pdf_na_tela(st.session_state['pdf_os_view'])
            with open(st.session_state['pdf_os_view'], "rb") as f:
                st.download_button("📥 BAIXAR OS PDF", f, f"OS_{num_os}.pdf", "application/pdf", use_container_width=True)
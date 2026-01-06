import streamlit as st
import pandas as pd
from utils.brasfort_pdf import RelatorioBrasfort
from utils.ia_auxiliar import melhorar_texto_com_ia

# --- MOTOR PDF ---
def gerar_pdf_cronograma(dados):
    pdf = RelatorioBrasfort(titulo="CRONOGRAMA TÉCNICO")
    
    # Capa
    subtitulo_capa = f"Cliente: {dados['cliente']}\nReferência: {dados['referencia']}"
    if dados['tipo'] == 'fases':
        titulo_principal = "CRONOGRAMA DE IMPLEMENTAÇÃO / PROJETO"
    else:
        titulo_principal = "CRONOGRAMA DE VISITAS E ACOMPANHAMENTO"

    pdf.gerar_capa(
        titulo_principal=titulo_principal,
        sub_titulo=subtitulo_capa,
        autor=dados['tecnico']
    )
    
    pdf.add_page()
    pdf.ln(20)

    # Cabeçalho Interno
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 6, f"Cliente: {dados['cliente']}", ln=True)
    pdf.set_font('Barlow', '', 12)
    pdf.cell(0, 6, f"Data Base: {dados['data']}", ln=True)
    pdf.ln(10)

    # --- 1. OBJETIVO / INTRODUÇÃO ---
    if dados['introducao']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "1. OBJETIVO E METODOLOGIA", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['introducao'], align='J')
        pdf.ln(10)

    # --- 2. CORPO DO CRONOGRAMA ---
    pdf.set_font('Barlow', 'B', 12)
    pdf.cell(0, 8, "2. DETALHAMENTO DO CRONOGRAMA", ln=True)
    pdf.ln(2)

    # === MODO A: TABELA (Estilo CIPLAN Visitas) ===
    if dados['tipo'] == 'tabela':
        if not dados['df_tabela'].empty:
            # Configurações visuais
            pdf.set_font('Barlow', 'B', 10)
            pdf.set_fill_color(10, 35, 80) # Azul Brasfort
            pdf.set_text_color(255, 255, 255)
            
            # Larguras: Local(80), Data(40), Status(40), Obs(30)
            cols = [("Local / Atividade", 80), ("Data Prevista", 35), ("Status", 35), ("Observação", 40)]
            
            # Cabeçalho
            for nome, larg in cols:
                pdf.cell(larg, 8, nome, 1, 0, 'C', True)
            pdf.ln()
            
            # Linhas
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Barlow', '', 10)
            
            for index, row in dados['df_tabela'].iterrows():
                fill = True if index % 2 == 0 else False
                pdf.set_fill_color(240, 240, 240) # Cinza claro
                
                # Tratamento de nulos
                local = str(row.get("Local / Atividade", ""))
                data = str(row.get("Data", ""))
                status = str(row.get("Status", ""))
                obs = str(row.get("Obs", ""))

                # Cor do Status (Visual bonito)
                pdf.set_text_color(0,0,0)
                if "Realizada" in status or "Concluído" in status:
                    pdf.set_text_color(0, 100, 0) # Verde
                elif "Pendente" in status or "Prevista" in status:
                    pdf.set_text_color(200, 100, 0) # Laranja

                pdf.cell(80, 8, local, 1, 0, 'L', fill)
                
                pdf.set_text_color(0,0,0) # Reset para preto
                pdf.cell(35, 8, data, 1, 0, 'C', fill)
                
                # Imprime status colorido
                if "Realizada" in status or "Concluído" in status:
                    pdf.set_text_color(0, 100, 0)
                elif "Pendente" in status or "Prevista" in status:
                    pdf.set_text_color(200, 100, 0)
                pdf.cell(35, 8, status, 1, 0, 'C', fill)
                
                pdf.set_text_color(0,0,0)
                pdf.cell(40, 8, obs, 1, 1, 'L', fill)

    # === MODO B: FASES (Estilo Longevitá / CIPLAN Unidades) ===
    else:
        for fase in dados['lista_fases']:
            # Título da Fase (Fundo Cinza)
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font('Barlow', 'B', 11)
            pdf.cell(0, 8, f" {fase['titulo'].upper()}", ln=True, fill=True, border='L')
            
            # Conteúdo da Fase
            pdf.set_font('Barlow', '', 11)
            pdf.multi_cell(0, 6, fase['conteudo'], align='J')
            pdf.ln(5)

    # --- 3. CONCLUSÃO / CONSIDERAÇÕES ---
    pdf.ln(5)
    if dados['conclusao']:
        pdf.set_font('Barlow', 'B', 12)
        pdf.cell(0, 8, "3. CONSIDERAÇÕES FINAIS", ln=True)
        pdf.set_font('Barlow', '', 11)
        pdf.multi_cell(0, 6, dados['conclusao'], align='J')

    pdf.bloco_assinatura(dados['tecnico'])
    
    nome_arquivo = f"Cronograma_{dados['cliente'].split()[0]}_{dados['data'].replace('/','-')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# --- INTERFACE ---
def renderizar_cronograma():
    st.subheader("📅 Gerador de Cronogramas")
    st.caption("Crie planejamentos por fases ou tabelas de acompanhamento.")

    # Seletor de Modo
    modo = st.radio("Tipo de Cronograma:", 
                    ["Tabela de Acompanhamento (Lista)", "Projeto por Fases (Etapas Detalhadas)"], 
                    horizontal=True)
    
    tipo = "tabela" if "Tabela" in modo else "fases"

    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Cliente", value="Grupo CIPLAN")
        referencia = st.text_input("Referência / Projeto", value="Modernização de Acesso")
    with col2:
        tecnico = st.text_input("Responsável", value="Luciano Pereira")
        data = st.date_input("Data Base").strftime("%d/%m/%Y")

    st.markdown("---")

    # --- INTRODUÇÃO ---
    st.write("**1. Introdução / Objetivo**")
    if "txt_crono_intro" not in st.session_state: st.session_state.txt_crono_intro = ""
    
    rascunho_intro = st.text_area("Objetivo do cronograma:", height=70, placeholder="Ex: Organizar as visitas técnicas nas unidades de GO e DF...", key="ras_intro")
    
    if st.button("Formalizar Introdução", key="btn_intro"):
        st.session_state.txt_crono_intro = melhorar_texto_com_ia(rascunho_intro, "Objetivo de Cronograma")
    
    intro_final = st.text_area("Texto Final (Introdução):", value=st.session_state.txt_crono_intro, height=100, key="fin_intro")

    st.markdown("---")
    st.write("**2. Estrutura do Cronograma**")

    # === LÓGICA DA INTERFACE DE TABELA ===
    df_final = pd.DataFrame()
    lista_fases_final = []

    if tipo == "tabela":
        st.info("💡 Dica: Preencha a tabela abaixo. Adicione linhas clicando no '+' da tabela.")
        
        # Cria um DataFrame inicial se não existir
        if "df_cronograma" not in st.session_state:
            st.session_state.df_cronograma = pd.DataFrame(
                [{"Local / Atividade": "Visita Técnica Inicial", "Data": "10/10/2025", "Status": "Realizada", "Obs": "Tudo OK"}],
            )

        # Editor de Dados (Tabela Editável)
        df_editado = st.data_editor(
            st.session_state.df_cronograma,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    options=["Agendada", "Realizada", "Pendente", "Cancelada"],
                    required=True,
                )
            }
        )
        df_final = df_editado

    # === LÓGICA DA INTERFACE DE FASES ===
    else:
        st.info("💡 Dica: Adicione blocos para cada fase (Ex: Fase 1, Fase 2). Use a IA para formatar as datas.")
        
        if "fases_cronograma" not in st.session_state:
            st.session_state.fases_cronograma = []

        # Botão para adicionar fase
        c_add1, c_add2 = st.columns([3, 1])
        with c_add1:
            nova_fase_titulo = st.text_input("Título da Nova Fase", placeholder="Ex: Fase 1 - Infraestrutura")
        with c_add2:
            st.write("")
            st.write("")
            if st.button("➕ Adicionar Fase"):
                if nova_fase_titulo:
                    st.session_state.fases_cronograma.append({"titulo": nova_fase_titulo, "conteudo": ""})
                    st.rerun()

        # Renderiza as fases existentes
        for i, fase in enumerate(st.session_state.fases_cronograma):
            with st.container(border=True):
                c_head1, c_head2 = st.columns([0.9, 0.1])
                c_head1.write(f"**{fase['titulo']}**")
                if c_head2.button("X", key=f"del_fase_{i}"):
                    st.session_state.fases_cronograma.pop(i)
                    st.rerun()
                
                # Conteúdo da Fase
                txt_fase = st.text_area(f"Atividades da {fase['titulo']}", value=fase['conteudo'], height=100, key=f"txt_fase_{i}")
                
                # IA para formatar datas dentro da fase
                if st.button(f"✨ Formatar Datas ({fase['titulo']})", key=f"ia_fase_{i}"):
                    prompt = f"Formate este texto como uma lista cronológica de atividades. Mantenha as datas. Texto: {txt_fase}"
                    novo_texto = melhorar_texto_com_ia(prompt, "Lista Cronológica")
                    st.session_state.fases_cronograma[i]['conteudo'] = novo_texto
                    st.rerun()
                
                # Atualiza o estado se o usuário digitar manualmente
                if txt_fase != fase['conteudo']:
                    st.session_state.fases_cronograma[i]['conteudo'] = txt_fase

        lista_fases_final = st.session_state.fases_cronograma

    # --- CONCLUSÃO ---
    st.markdown("---")
    st.write("**3. Considerações Finais**")
    if "txt_crono_conc" not in st.session_state: st.session_state.txt_crono_conc = ""
    
    rascunho_conc = st.text_area("Resumo final:", height=70, placeholder="Ex: O cronograma está sujeito a chuvas...", key="ras_conc")
    
    if st.button("Formalizar Conclusão", key="btn_conc"):
        st.session_state.txt_crono_conc = melhorar_texto_com_ia(rascunho_conc, "Conclusão Cronograma")
    
    conc_final = st.text_area("Texto Final (Conclusão):", value=st.session_state.txt_crono_conc, height=80, key="fin_conc")

    # --- GERAR ---
    if st.button("Gerar Cronograma PDF", type="primary"):
        dados = {
            "tipo": tipo,
            "cliente": cliente, "referencia": referencia, "tecnico": tecnico, "data": data,
            "introducao": intro_final,
            "df_tabela": df_final,       # Usado se for tabela
            "lista_fases": lista_fases_final, # Usado se for fases
            "conclusao": conc_final
        }

        try:
            arquivo = gerar_pdf_cronograma(dados)
            st.session_state['crono_pronto'] = arquivo
            st.success("Cronograma Gerado com Sucesso!")
        except Exception as e:
            st.error(f"Erro: {e}")

    if 'crono_pronto' in st.session_state:
        with open(st.session_state['crono_pronto'], "rb") as f:
            st.download_button("📥 Baixar Cronograma", f, file_name="Cronograma.pdf")
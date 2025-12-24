import google.generativeai as genai
import streamlit as st
import time
import random

# --- CONFIGURAÇÃO ---
def configurar_api():
    try:
        if "GOOGLE_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
            return True
    except:
        pass
    return False

# Modelos (Principal e Reserva)
MODELO_PRINCIPAL = "gemini-2.5-flash"
MODELO_BACKUP = "gemini-1.5-flash"

def melhorar_texto_com_ia(texto_usuario, tipo_documento="Relatório Técnico"):
    """
    Função focada puramente em TEXTUALIZAÇÃO.
    Transforma texto informal em formal, sem buscar dados externos.
    """
    if not configurar_api():
        return "Erro: Chave de API não configurada no secrets.toml"

    # Prompt focado na escrita técnica
    instrucao = f"""
    Atue como um Supervisor Técnico Sênior da Brasfort.
    Sua única função é reescrever o texto abaixo para torná-lo profissional, formal e técnico.
    
    Regras:
    1. Corrija português, pontuação e concordância.
    2. Substitua gírias por termos técnicos (ex: "fio solto" -> "cabeamento desconectado").
    3. Seja direto e impessoal (ex: "Foi realizado..." em vez de "Eu fiz...").
    4. Mantenha o sentido original da mensagem.
    
    Contexto: Este texto entrará em um {tipo_documento}.
    
    Texto Original: "{texto_usuario}"
    
    Texto Melhorado:
    """

    # Lógica de Tentativa (Try/Except) para não travar
    try:
        model = genai.GenerativeModel(MODELO_PRINCIPAL)
        response = model.generate_content(instrucao)
        return response.text
    except Exception as e:
        erro_str = str(e)
        # Se for erro de cota (429), tenta o backup
        if "429" in erro_str or "quota" in erro_str.lower():
            try:
                time.sleep(1)
                model_bkp = genai.GenerativeModel(MODELO_BACKUP)
                response = model_bkp.generate_content(instrucao)
                return response.text
            except:
                return f"Erro na IA (Backup falhou): {e}"
        else:
            return f"Erro na IA: {e}"

# Mantemos essa função vazia ou simples para não quebrar outros módulos que a chamem
def ler_exemplos_pasta():
    return ""
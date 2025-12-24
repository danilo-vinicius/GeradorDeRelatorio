import os
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import random

# Configura a chave do Google
try:
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Configuração do modelo (Temperatura baixa = mais formal/técnico)
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
        # Usamos o Gemini 1.5 Flash que é rápido e ótimo para texto
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            generation_config=generation_config,
        )
    else:
        model = None
except Exception as e:
    model = None
    print(f"Erro ao configurar Gemini: {e}")

def ler_exemplos_pasta():
    """Lê aleatoriamente 3 PDFs da pasta estudo_relatorios para usar como contexto."""
    pasta = "estudo_relatorios"
    texto_contexto = ""
    
    if not os.path.exists(pasta):
        return "Nenhum exemplo encontrado (pasta não existe)."

    arquivos = [f for f in os.listdir(pasta) if f.endswith('.pdf')]
    
    if not arquivos:
        return "Nenhum PDF de exemplo encontrado."

    # Seleciona até 3 arquivos para dar contexto sem exagerar
    amostra = random.sample(arquivos, min(len(arquivos), 3))

    for arquivo in amostra:
        try:
            reader = PdfReader(os.path.join(pasta, arquivo))
            texto_pdf = ""
            # Lê apenas a primeira página (resumo/introdução)
            for page in reader.pages[:1]: 
                texto_pdf += page.extract_text()
            texto_contexto += f"\n--- EXEMPLO REAL ({arquivo}) ---\n{texto_pdf}\n"
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
            
    return texto_contexto

def melhorar_texto_com_ia(texto_rascunho, tipo_relatorio):
    """Envia o rascunho para o Gemini reescrever."""
    
    if not model:
        return "ERRO: Chave do Google não configurada no secrets.toml"

    exemplos = ler_exemplos_pasta()

    # O Prompt (Instrução) para o Gemini
    prompt_completo = f"""
    Você é um Supervisor Técnico da BRASFORT. 
    Sua tarefa é reescrever o relato informal abaixo para um padrão técnico, formal e culto.
    
    TIPO DE RELATÓRIO: {tipo_relatorio}
    
    DIRETRIZES:
    1. Corrija erros gramaticais.
    2. Use termos técnicos da área de segurança eletrônica (CFTV, LPR, Redes).
    3. Use voz passiva ("Foi identificado" ao invés de "Eu vi").
    4. Seja direto e profissional.
    
    Abaixo estão exemplos de como escrevemos na empresa (para você copiar o estilo):
    {exemplos}
    
    ---
    RASCUNHO INFORMAL (Reescreva isto):
    "{texto_rascunho}"
    
    RESPOSTA REESCRITA (Apenas o texto técnico):
    """

    try:
        # Chama o Gemini
        response = model.generate_content(prompt_completo)
        return response.text.strip()
    except Exception as e:
        return f"Erro ao conectar com Gemini: {e}"
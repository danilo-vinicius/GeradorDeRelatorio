import google.generativeai as genai

# COLE SUA CHAVE AQUI PARA TESTAR
CHAVE = "AIzaSyDrgjLf7FOoeqLurANF6qFbiBybpm01lLY" 

genai.configure(api_key=CHAVE)

print("--- CONSULTANDO MODELOS DISPONÍVEIS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Erro ao listar: {e}")
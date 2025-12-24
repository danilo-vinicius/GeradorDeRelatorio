import os

pasta = "estudo_relatorios"

print(f"--- LISTANDO ARQUIVOS NA PASTA '{pasta}' ---\n")

try:
    arquivos = [f for f in os.listdir(pasta) if f.lower().endswith('.pdf')]
    arquivos.sort() # Organiza em ordem alfabética
    
    print(f"Total encontrado: {len(arquivos)} arquivos.\n")
    
    for arquivo in arquivos:
        print(arquivo)
        
except FileNotFoundError:
    print(f"Erro: A pasta '{pasta}' não foi encontrada.")
except Exception as e:
    print(f"Erro: {e}")
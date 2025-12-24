import os

def listar_equipamentos_cadastrados():
    """Lê a pasta 'estudo_equipamentos' e retorna uma lista de nomes limpos."""
    pasta = "estudo_equipamentos"
    lista = []
    
    if not os.path.exists(pasta):
        return []

    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".txt"):
            try:
                # O nome do arquivo é tipo: EQ_123_Intelbras_MHDX_3004.txt
                # Vamos limpar para ficar bonito na tela
                # Removemos EQ_123_ e a extensão .txt
                partes = arquivo.replace(".txt", "").split("_")
                
                # Reconstrói o nome (Marca + Modelo)
                # partes[0] é 'EQ', partes[1] é ID. Começamos do 2.
                if len(partes) > 2:
                    nome_limpo = " ".join(partes[2:])
                    lista.append(nome_limpo)
            except:
                continue
                
    return sorted(lista)
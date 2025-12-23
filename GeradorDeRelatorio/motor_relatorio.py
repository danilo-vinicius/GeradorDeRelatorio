from fpdf import FPDF
from datetime import datetime
import os

class RelatorioLPR(FPDF):
    def header(self):
        # Aqui iria o Logo da sua empresa (descomente se tiver um arquivo logo.png)
        # self.image('logo.png', 10, 8, 33)
        
        self.set_font('Arial', 'B', 15)
        # Título
        self.cell(0, 10, 'Relatório de Ocorrência - Sistema LPR', ln=True, align='C')
        self.ln(10) # Quebra de linha de 10mm

    def footer(self):
        # Posição a 1.5cm de baixo
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Número da página
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

def calcular_tempo(inicio_str, fim_str):
    """Calcula a diferença entre dois horários no formato HH:MM:SS"""
    formato = "%H:%M:%S"
    t_inicio = datetime.strptime(inicio_str, formato)
    t_fim = datetime.strptime(fim_str, formato)
    delta = t_fim - t_inicio
    return str(delta)

def gerar_relatorio_lpr(dados):
    pdf = RelatorioLPR()
    pdf.add_page()
    
    # --- DADOS DO CLIENTE ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Cliente: {dados['cliente']}", ln=True)
    pdf.cell(0, 10, f"Data da Ocorrência: {dados['data']}", ln=True)
    
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Placa do Veículo: {dados['placa']}", ln=True)
    pdf.ln(5)

    # --- ANÁLISE TEMPORAL ---
    # Calculando os tempos automaticamente
    tempo_leitura = calcular_tempo(dados['hora_chegada'], dados['hora_leitura'])
    tempo_total = calcular_tempo(dados['hora_chegada'], dados['hora_abertura'])

    pdf.set_fill_color(240, 240, 240) # Fundo cinza claro
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, "Análise de Tempos:", ln=True, fill=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(50, 8, f"Chegada: {dados['hora_chegada']}", border=1)
    pdf.cell(50, 8, f"Leitura: {dados['hora_leitura']}", border=1)
    pdf.cell(50, 8, f"Abertura: {dados['hora_abertura']}", border=1)
    pdf.ln(10)
    
    # Resultado do calculo
    pdf.set_text_color(200, 0, 0) # Texto vermelho para destaque
    pdf.cell(0, 10, f"Tempo total de processo: {tempo_total} (Chegada até Abertura)", ln=True)
    pdf.set_text_color(0, 0, 0) # Volta para preto
    pdf.ln(5)

    # --- EVIDÊNCIAS (IMAGENS) ---
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, "Evidências Visuais:", ln=True)
    
    # Configuração para 3 imagens alinhadas ou uma abaixo da outra
    # Aqui vamos colocar uma abaixo da outra para garantir tamanho legível
    
    lista_imgs = [
        ("Momento da Chegada", dados['img_chegada']),
        ("Momento da Leitura LPR", dados['img_leitura']),
        ("Abertura do Portão", dados['img_abertura'])
    ]

    for titulo, caminho_img in lista_imgs:
        if os.path.exists(caminho_img):
            pdf.set_font('Arial', 'I', 10)
            pdf.cell(0, 8, titulo, ln=True)
            # Adiciona imagem (x=centralizado mais ou menos, w=largura)
            # w=100 significa 10cm de largura
            pdf.image(caminho_img, x=10, w=100) 
            pdf.ln(5)
        else:
            pdf.cell(0, 10, f"[ERRO: Imagem não encontrada: {caminho_img}]", ln=True)

    # --- SALVAR ---
    nome_arquivo = f"Relatorio_{dados['cliente'].replace(' ', '_')}_{dados['placa']}.pdf"
    pdf.output(nome_arquivo)
    
    return nome_arquivo

# --- TESTE DO MOTOR ---
# Vamos simular os dados que viriam da interface depois
dados_simulados = {
    "cliente": "Condomínio Cerejeiras",
    "data": "22/12/2025",
    "placa": "ABC-1234",
    "hora_chegada": "14:10:05",
    "hora_leitura": "14:10:15",
    "hora_abertura": "14:10:25",
    # Certifique-se de ter imagens com esses nomes na pasta ou troque os nomes abaixo
    "img_chegada": "foto1.jpg", 
    "img_leitura": "foto2.jpg",
    "img_abertura": "foto3.jpg"
}

if __name__ == "__main__":
    gerar_relatorio_lpr(dados_simulados)
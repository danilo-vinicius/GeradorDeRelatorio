from fpdf import FPDF
import os
from datetime import datetime

class RelatorioBrasfort(FPDF):
    def __init__(self, titulo="RELATÓRIO TÉCNICO"):
        super().__init__()
        self.titulo_relatorio = titulo
        self.is_cover_page = False  # Flag para saber se é capa
        
        # Caminhos
        self.font_path_reg = "assets/fonts/Barlow-Regular.ttf"
        self.font_path_bold = "assets/fonts/Barlow-Bold.ttf"
        
        # Tenta carregar SVG ou PNG
        if os.path.exists("assets/logo.svg"):
            self.logo_path = "assets/logo.svg"
        else:
            self.logo_path = "assets/logo.png"

        # Carregando Fontes
        if os.path.exists(self.font_path_reg):
            self.add_font('Barlow', '', self.font_path_reg)
        if os.path.exists(self.font_path_bold):
            self.add_font('Barlow', 'B', self.font_path_bold)
            
        self.set_font('Barlow' if os.path.exists(self.font_path_reg) else 'Arial', '', 12)

    def header(self):
        # Se for capa, não desenha o cabeçalho padrão
        if self.is_cover_page:
            return

        # Logo pequeno no canto
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, w=30)
        
        # Título Dinâmico
        self.set_y(15)
        self.set_x(45) 
        self.set_font('Barlow' if os.path.exists(self.font_path_bold) else 'Arial', 'B', 16)
        self.cell(0, 10, self.titulo_relatorio.upper(), ln=True, align='L')
        self.ln(10)

    def footer(self):
        # Se for capa, não desenha o rodapé padrão
        if self.is_cover_page:
            return

        self.set_y(-28)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

        self.set_font('Barlow' if os.path.exists(self.font_path_reg) else 'Arial', '', 8)
        self.set_text_color(100, 100, 100)
        
        self.cell(0, 4, "BRASFORT - Segurança Eletrônica", ln=True, align='C')
        self.cell(0, 4, "SAAN Quadra 03 nº 1240, Zona Industrial - Brasília/DF", ln=True, align='C')
        self.cell(0, 4, "(61) 3878-3434 | brasfort.com.br", ln=True, align='C')
        
        self.set_y(-10)
        self.cell(0, 10, f'Página {self.page_no()}', align='R')

    def bloco_assinatura(self, nome_tecnico):
        self.ln(15)
        if self.get_y() > 250:
            self.add_page()
            
        self.set_font('Barlow' if os.path.exists(self.font_path_bold) else 'Arial', 'B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, "Elaborado por:", ln=True)
        
        self.set_font('Barlow' if os.path.exists(self.font_path_reg) else 'Arial', '', 11)
        self.cell(0, 5, nome_tecnico, ln=True)
        self.cell(0, 5, "Segurança Eletrônica - BRASFORT", ln=True)

    # --- CAPA CORRIGIDA ---
    def gerar_capa(self, titulo_principal, sub_titulo, autor="Técnico Responsável"):
        # 1. DESLIGA QUEBRA AUTOMÁTICA (Isso resolve a página em branco!)
        self.set_auto_page_break(False)
        self.is_cover_page = True 
        self.add_page()

        # 2. DESIGN DA CAPA
        # Barra Lateral
        self.set_fill_color(10, 35, 80) # Azul Escuro
        self.rect(0, 0, 8, 50, 'F') 
        self.set_fill_color(220, 190, 110) # Dourado
        self.rect(0, 50, 8, 297-50, 'F') 

        # Logo
        self.set_y(15)
        self.set_x(20)
        if os.path.exists(self.logo_path):
            self.image(self.logo_path, w=45)

        # Frase
        self.set_y(18)
        self.set_x(120)
        self.set_font('Barlow' if os.path.exists(self.font_path_reg) else 'Arial', '', 9)
        self.set_text_color(180, 160, 100)
        self.cell(80, 5, "Serviços também têm marca.", align='R', ln=True)

        # Título
        self.set_y(110)
        self.set_x(25)
        self.set_font('Barlow' if os.path.exists(self.font_path_bold) else 'Arial', 'B', 24)
        self.set_text_color(0, 0, 0)
        self.multi_cell(170, 10, titulo_principal, align='L')
        
        # Subtítulo
        self.ln(2)
        self.set_x(25)
        self.set_font('Barlow', '', 14)
        self.set_text_color(80, 80, 80)
        self.multi_cell(170, 8, sub_titulo, align='L')

        # Data
        self.set_y(230)
        self.set_x(25)
        self.set_font('Barlow', '', 10)
        self.cell(0, 5, datetime.now().strftime("Data: %d de %B de %Y"), ln=True)

        # Rodapé da Capa
        self.set_y(-20)
        
        self.set_x(20)
        self.set_font('Barlow', 'B', 10)
        self.set_text_color(10, 35, 80)
        self.cell(30, 5, "(61) 3878-3434", align='L')
        
        self.set_draw_color(10, 35, 80)
        self.line(52, self.get_y(), 52, self.get_y()+5)
        
        self.set_x(55)
        self.set_font('Barlow', '', 8)
        self.set_text_color(80, 80, 80)
        self.cell(100, 5, "SAAN Quadra 03 nº 1240, Zona Industrial - Brasília/DF - 70.632-320", align='L')

        self.set_x(160)
        self.set_font('Barlow', 'B', 10)
        self.set_text_color(10, 35, 80)
        self.cell(40, 5, "brasfort.com.br", align='R')

        # 3. LIGA A QUEBRA AUTOMÁTICA DE VOLTA (Para o resto do relatório)
        self.is_cover_page = False 
        self.set_auto_page_break(True, margin=20)
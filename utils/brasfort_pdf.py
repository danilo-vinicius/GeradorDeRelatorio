from fpdf import FPDF
import os
from datetime import datetime

class RelatorioBrasfort(FPDF):
    def __init__(self, titulo="RELATÓRIO TÉCNICO"):
        super().__init__()
        self.titulo_documento = titulo
        self.is_cover_page = False  # Flag para controlar o cabeçalho
        
        # Caminhos das fontes
        self.font_path_reg = "assets/fonts/Barlow-Regular.ttf"
        self.font_path_bold = "assets/fonts/Barlow-Bold.ttf"
        
        # LÓGICA DO LOGO: Prioriza SVG, senão usa PNG
        if os.path.exists("assets/logo.svg"):
            self.logo_path = "assets/logo.svg"
        else:
            self.logo_path = "assets/logo.png"

        # Carregando Fontes
        self.use_custom_font = False
        try:
            if os.path.exists(self.font_path_reg) and os.path.exists(self.font_path_bold):
                self.add_font('Barlow', '', self.font_path_reg, uni=True)
                self.add_font('Barlow', 'B', self.font_path_bold, uni=True)
                self.add_font('Barlow', 'I', 'assets/fonts/Barlow-Italic.ttf', uni=True)
                self.use_custom_font = True
        except:
            pass 

    def _set_font(self, style='', size=12):
        """Helper para usar a fonte certa (Barlow ou Arial)"""
        family = 'Barlow' if self.use_custom_font else 'Arial'
        self.set_font(family, style, size)

    def header(self):
        # TRAVA DE CABEÇALHO: Se a flag de capa estiver ativa, não desenha
        if self.is_cover_page:
            return

        # LOGO
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, 10, 8, 33)
            except:
                pass 
            
        # Título do Relatório
        self._set_font('B', 10)
        self.set_text_color(10, 35, 80)
        self.cell(0, 10, self.titulo_documento, 0, 1, 'R')
        self.ln(5)

        # Linha fina
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        # TRAVA DE RODAPÉ (CORRIGIDA): 
        # Se for a Página 1 (Capa), NUNCA desenha o rodapé padrão.
        if self.page_no() == 1:
            return

        self.set_y(-25)
        
        # Linha fina
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        
        self._set_font('', 8)
        self.set_text_color(100, 100, 100)
        
        # Informações
        self.cell(0, 4, 'BRASFORT - Segurança Eletrônica', 0, 1, 'C')
        texto_rodape = "SAAN Quadra 03 nº 1240, Zona Industrial - Brasília/DF  |  (61) 3878-3434  |  brasfort.com.br"
        self.cell(0, 4, texto_rodape, 0, 1, 'C')
        
        # Paginação
        self.set_y(-15)
        self._set_font('I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'R')

    def bloco_assinatura(self, nome_tecnico):
        self.ln(15)
        if self.get_y() > 240:
            self.add_page()
            
        self._set_font('B', 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 5, "Elaborado por:", ln=True)
        self.ln(5)
        
        self._set_font('', 11)
        self.cell(0, 5, nome_tecnico, ln=True)
        self.cell(0, 5, "Segurança Eletrônica - BRASFORT", ln=True)

    def gerar_capa(self, titulo_principal, sub_titulo, autor="Técnico Responsável"):
        # 1. ATIVA MODO CAPA (Para travar o header)
        self.is_cover_page = True 
        self.set_auto_page_break(False) 
        self.add_page()

        # Design (Faixa Dourada/Azul)
        self.set_fill_color(10, 35, 80) # Azul Escuro
        self.rect(0, 0, 5, 50, 'F') 
        self.set_fill_color(220, 190, 110) # Dourado
        self.rect(0, 50, 5, 297-50, 'F') 

        # Logo Grande
        self.set_y(20)
        self.set_x(20)
        if self.logo_path and os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, w=50)
            except:
                pass

        # Frase
        self.set_y(25)
        self.set_x(120)
        self._set_font('', 9)
        self.set_text_color(150, 150, 150)
        self.cell(80, 5, "Serviços também têm marca.", align='R', ln=True)

        # Títulos
        self.set_y(100)
        self.set_x(20)
        self._set_font('B', 26)
        self.set_text_color(10, 35, 80)
        self.multi_cell(170, 12, titulo_principal, align='L')
        
        self.ln(5)
        self.set_x(20)
        self._set_font('', 14)
        self.set_text_color(80, 80, 80)
        self.multi_cell(170, 8, sub_titulo, align='L')

        # Data
        meses = {1:'janeiro', 2:'fevereiro', 3:'março', 4:'abril', 5:'maio', 6:'junho',
                 7:'julho', 8:'agosto', 9:'setembro', 10:'outubro', 11:'novembro', 12:'dezembro'}
        hoje = datetime.now()
        data_extenso = f"Brasília, {hoje.day} de {meses[hoje.month]} de {hoje.year}"
        
        self.set_y(-40)
        self.set_x(20)
        self._set_font('', 11)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"{data_extenso}", ln=True)

        # Rodapé EXCLUSIVO da Capa
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(2)
        self.set_x(0)
        self._set_font('B', 9)
        self.set_text_color(10, 35, 80)
        
        contato = "(61) 3878-3434   |   SAAN Quadra 03 nº 1240, Zona Industrial - Brasília/DF   |   brasfort.com.br"
        self.cell(210, 5, contato, 0, 0, 'C')

        # Reset cursor
        self.set_y(0)

        # 2. DESATIVA MODO CAPA (Para as próximas páginas terem header)
        self.is_cover_page = False 
        self.set_auto_page_break(True, margin=20)
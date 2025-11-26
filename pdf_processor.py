"""
Módulo para procesar y extraer texto de documentos PDF
"""
import pdfplumber
from typing import List, Dict
import re


class PDFProcessor:
    """Clase para procesar documentos PDF y extraer su contenido"""
    
    def __init__(self):
        self.processed_texts = {}
    
    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extrae texto de un PDF y retorna información estructurada
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Dict con texto completo, páginas, y metadatos
        """
        text_content = []
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # Limpiar y normalizar texto
                        cleaned_text = self._clean_text(page_text)
                        text_content.append(cleaned_text)
                        pages_data.append({
                            'page': page_num,
                            'text': cleaned_text,
                            'lines': cleaned_text.split('\n')
                        })
                
                full_text = '\n'.join(text_content)
                
                return {
                    'full_text': full_text,
                    'pages': pages_data,
                    'total_pages': total_pages,
                    'total_lines': len(full_text.split('\n')),
                    'total_chars': len(full_text)
                }
        except Exception as e:
            raise Exception(f"Error al procesar PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza el texto extraído
        
        Args:
            text: Texto crudo del PDF
            
        Returns:
            Texto limpio y normalizado
        """
        if not text:
            return ""
        
        # Eliminar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        
        # Eliminar espacios al inicio y final de líneas
        lines = [line.strip() for line in text.split('\n')]
        
        # Eliminar líneas vacías múltiples
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if line:
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                cleaned_lines.append('')
                prev_empty = True
        
        return '\n'.join(cleaned_lines)
    
    def extract_structured_sections(self, pdf_path: str) -> List[Dict]:
        """
        Intenta identificar secciones estructuradas en el documento
        (artículos, capítulos, etc.)
        
        Args:
            pdf_path: Ruta al archivo PDF
            
        Returns:
            Lista de secciones identificadas
        """
        content = self.extract_text(pdf_path)
        sections = []
        
        # Patrones comunes para identificar secciones
        section_patterns = [
            r'^(Artículo\s+\d+)',
            r'^(CAPÍTULO\s+[IVX]+)',
            r'^(TÍTULO\s+[IVX]+)',
            r'^(Sección\s+\d+)',
            r'^(\d+\.\s+[A-Z])',
        ]
        
        lines = content['full_text'].split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            for pattern in section_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if current_section:
                        sections.append(current_section)
                    
                    current_section = {
                        'title': line,
                        'start_line': i,
                        'content': []
                    }
                    break
            
            if current_section:
                current_section['content'].append(line)
        
        if current_section:
            sections.append(current_section)
        
        return sections


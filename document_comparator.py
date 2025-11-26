"""
Módulo para comparar documentos y detectar diferencias
"""
import difflib
from typing import List, Dict, Tuple
from pdf_processor import PDFProcessor


class DocumentComparator:
    """Clase para comparar dos documentos y encontrar diferencias"""
    
    def __init__(self):
        self.processor = PDFProcessor()
    
    def compare_documents(self, pdf1_path: str, pdf2_path: str) -> Dict:
        """
        Compara dos documentos PDF y retorna las diferencias
        
        Args:
            pdf1_path: Ruta al primer PDF
            pdf2_path: Ruta al segundo PDF
            
        Returns:
            Dict con diferencias encontradas
        """
        # Extraer texto de ambos documentos
        doc1 = self.processor.extract_text(pdf1_path)
        doc2 = self.processor.extract_text(pdf2_path)
        
        # Dividir en líneas para comparación
        lines1 = doc1['full_text'].split('\n')
        lines2 = doc2['full_text'].split('\n')
        
        # Usar difflib para encontrar diferencias
        differ = difflib.SequenceMatcher(None, lines1, lines2)
        
        # Obtener diferencias
        differences = self._get_differences(lines1, lines2, differ)
        
        # Calcular estadísticas
        stats = self._calculate_statistics(doc1, doc2, differences)
        
        return {
            'document1': {
                'path': pdf1_path,
                'total_pages': doc1['total_pages'],
                'total_lines': doc1['total_lines'],
                'total_chars': doc1['total_chars']
            },
            'document2': {
                'path': pdf2_path,
                'total_pages': doc2['total_pages'],
                'total_lines': doc2['total_lines'],
                'total_chars': doc2['total_chars']
            },
            'differences': differences,
            'statistics': stats,
            'similarity_ratio': differ.ratio()
        }
    
    def _get_differences(self, lines1: List[str], lines2: List[str], 
                        differ: difflib.SequenceMatcher) -> List[Dict]:
        """
        Extrae las diferencias entre dos listas de líneas
        
        Args:
            lines1: Líneas del primer documento
            lines2: Líneas del segundo documento
            differ: SequenceMatcher con la comparación
            
        Returns:
            Lista de diferencias encontradas
        """
        differences = []
        
        for tag, i1, i2, j1, j2 in differ.get_opcodes():
            if tag == 'replace':
                # Líneas modificadas
                differences.append({
                    'type': 'modified',
                    'position': i1,
                    'old_lines': lines1[i1:i2],
                    'new_lines': lines2[j1:j2],
                    'context': self._get_context(lines1, lines2, i1, j1)
                })
            elif tag == 'delete':
                # Líneas eliminadas
                differences.append({
                    'type': 'deleted',
                    'position': i1,
                    'lines': lines1[i1:i2],
                    'context': self._get_context(lines1, lines2, i1, i1)
                })
            elif tag == 'insert':
                # Líneas agregadas
                differences.append({
                    'type': 'added',
                    'position': j1,
                    'lines': lines2[j1:j2],
                    'context': self._get_context(lines1, lines2, i1, j1)
                })
        
        return differences
    
    def _get_context(self, lines1: List[str], lines2: List[str], 
                     pos1: int, pos2: int, context_size: int = 3) -> Dict:
        """
        Obtiene el contexto alrededor de una diferencia
        
        Args:
            lines1: Líneas del primer documento
            lines2: Líneas del segundo documento
            pos1: Posición en el primer documento
            pos2: Posición en el segundo documento
            context_size: Número de líneas de contexto
            
        Returns:
            Dict con contexto antes y después
        """
        return {
            'before_doc1': lines1[max(0, pos1 - context_size):pos1],
            'after_doc1': lines1[pos1:min(len(lines1), pos1 + context_size)],
            'before_doc2': lines2[max(0, pos2 - context_size):pos2],
            'after_doc2': lines2[pos2:min(len(lines2), pos2 + context_size)]
        }
    
    def _calculate_statistics(self, doc1: Dict, doc2: Dict, 
                             differences: List[Dict]) -> Dict:
        """
        Calcula estadísticas de la comparación
        
        Args:
            doc1: Datos del primer documento
            doc2: Datos del segundo documento
            differences: Lista de diferencias
            
        Returns:
            Dict con estadísticas
        """
        added_count = sum(1 for d in differences if d['type'] == 'added')
        deleted_count = sum(1 for d in differences if d['type'] == 'deleted')
        modified_count = sum(1 for d in differences if d['type'] == 'modified')
        
        total_added_lines = sum(len(d['lines']) for d in differences if d['type'] == 'added')
        total_deleted_lines = sum(len(d['lines']) for d in differences if d['type'] == 'deleted')
        
        return {
            'total_differences': len(differences),
            'added_sections': added_count,
            'deleted_sections': deleted_count,
            'modified_sections': modified_count,
            'total_added_lines': total_added_lines,
            'total_deleted_lines': total_deleted_lines,
            'pages_changed': self._estimate_pages_changed(differences, doc1, doc2)
        }
    
    def _estimate_pages_changed(self, differences: List[Dict], 
                               doc1: Dict, doc2: Dict) -> int:
        """
        Estima cuántas páginas fueron afectadas por los cambios
        """
        if not differences:
            return 0
        
        # Estimación simple basada en líneas cambiadas
        total_changes = sum(
            len(d.get('lines', [])) + len(d.get('old_lines', [])) + len(d.get('new_lines', []))
            for d in differences
        )
        
        avg_lines_per_page = (doc1['total_lines'] + doc2['total_lines']) / 2 / max(doc1['total_pages'], doc2['total_pages'], 1)
        estimated_pages = int(total_changes / max(avg_lines_per_page, 1)) + 1
        
        return min(estimated_pages, max(doc1['total_pages'], doc2['total_pages']))


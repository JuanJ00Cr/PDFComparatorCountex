"""
Módulo de chatbot para interactuar con los documentos comparados
"""
import os
from openai import OpenAI
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class DocumentChatbot:
    """Chatbot especializado en responder preguntas sobre documentos comparados"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Modelo preciso y eficiente
        self.conversation_history = []
    
    def ask_question(self, question: str, comparison_result: Dict, 
                    document_texts: Dict[str, str]) -> str:
        """
        Responde una pregunta sobre los documentos comparados
        
        Args:
            question: Pregunta del usuario
            comparison_result: Resultado de la comparación de documentos
            document_texts: Textos completos de ambos documentos
            
        Returns:
            Respuesta del chatbot
        """
        # Preparar contexto completo de los documentos
        context = self._prepare_document_context(comparison_result, document_texts)
        
        # Preparar mensajes del sistema y usuario
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": f"{context}\n\nPregunta del usuario: {question}"
            }
        ]
        
        # Agregar historial de conversación reciente (últimas 3 preguntas)
        if self.conversation_history:
            recent_history = self.conversation_history[-6:]  # Últimas 3 preguntas y respuestas
            messages = [messages[0]] + recent_history + [messages[1]]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,  # Baja temperatura para respuestas más precisas
                max_tokens=1500
            )
            
            answer = response.choices[0].message.content
            
            # Guardar en historial
            self.conversation_history.append({
                "role": "user",
                "content": question
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            # Limitar historial a 20 mensajes
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return answer
            
        except Exception as e:
            return f"Error al generar respuesta: {str(e)}"
    
    def _prepare_document_context(self, comparison_result: Dict, 
                                 document_texts: Dict[str, str]) -> str:
        """
        Prepara el contexto completo de los documentos para el chatbot
        
        Args:
            comparison_result: Resultado de la comparación
            document_texts: Textos completos de ambos documentos
            
        Returns:
            Contexto formateado
        """
        context_parts = []
        
        # Información general de los documentos
        doc1_info = comparison_result.get('document1', {})
        doc2_info = comparison_result.get('document2', {})
        stats = comparison_result.get('statistics', {})
        
        context_parts.append("=== INFORMACIÓN DE LOS DOCUMENTOS ===")
        context_parts.append(f"\nDocumento 1:")
        context_parts.append(f"- Páginas: {doc1_info.get('total_pages', 'N/A')}")
        context_parts.append(f"- Líneas: {doc1_info.get('total_lines', 'N/A')}")
        context_parts.append(f"- Caracteres: {doc1_info.get('total_chars', 'N/A')}")
        
        context_parts.append(f"\nDocumento 2:")
        context_parts.append(f"- Páginas: {doc2_info.get('total_pages', 'N/A')}")
        context_parts.append(f"- Líneas: {doc2_info.get('total_lines', 'N/A')}")
        context_parts.append(f"- Caracteres: {doc2_info.get('total_chars', 'N/A')}")
        
        context_parts.append(f"\n=== ESTADÍSTICAS DE COMPARACIÓN ===")
        context_parts.append(f"- Similitud: {comparison_result.get('similarity_ratio', 0):.2%}")
        context_parts.append(f"- Total de diferencias: {stats.get('total_differences', 0)}")
        context_parts.append(f"- Secciones agregadas: {stats.get('added_sections', 0)}")
        context_parts.append(f"- Secciones eliminadas: {stats.get('deleted_sections', 0)}")
        context_parts.append(f"- Secciones modificadas: {stats.get('modified_sections', 0)}")
        
        # Diferencias principales (limitadas para no exceder tokens)
        differences = comparison_result.get('differences', [])[:15]
        if differences:
            context_parts.append(f"\n=== PRINCIPALES DIFERENCIAS ENCONTRADAS ===")
            for i, diff in enumerate(differences[:10], 1):
                context_parts.append(f"\n--- Diferencia {i} ({diff.get('type', 'unknown')}) ---")
                
                if diff.get('type') == 'added':
                    lines = diff.get('lines', [])[:3]
                    context_parts.append("Contenido agregado:")
                    for line in lines:
                        context_parts.append(f"  + {line[:200]}")  # Limitar longitud
                
                elif diff.get('type') == 'deleted':
                    lines = diff.get('lines', [])[:3]
                    context_parts.append("Contenido eliminado:")
                    for line in lines:
                        context_parts.append(f"  - {line[:200]}")
                
                elif diff.get('type') == 'modified':
                    old_lines = diff.get('old_lines', [])[:2]
                    new_lines = diff.get('new_lines', [])[:2]
                    context_parts.append("Contenido modificado:")
                    context_parts.append("Antes:")
                    for line in old_lines:
                        context_parts.append(f"  - {line[:200]}")
                    context_parts.append("Después:")
                    for line in new_lines:
                        context_parts.append(f"  + {line[:200]}")
        
        # Textos completos de los documentos (muestras representativas)
        context_parts.append(f"\n=== CONTENIDO DEL DOCUMENTO 1 (muestra) ===")
        doc1_text = document_texts.get('document1', '')
        if doc1_text:
            # Tomar primeras 2000 caracteres y últimas 1000 para contexto
            sample1 = doc1_text[:2000] + "\n...\n" + doc1_text[-1000:] if len(doc1_text) > 3000 else doc1_text
            context_parts.append(sample1)
        
        context_parts.append(f"\n=== CONTENIDO DEL DOCUMENTO 2 (muestra) ===")
        doc2_text = document_texts.get('document2', '')
        if doc2_text:
            sample2 = doc2_text[:2000] + "\n...\n" + doc2_text[-1000:] if len(doc2_text) > 3000 else doc2_text
            context_parts.append(sample2)
        
        return "\n".join(context_parts)
    
    def _get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema para el chatbot
        """
        return """Eres un asistente experto en análisis de documentos legales y reglamentarios. 
Tu tarea es responder preguntas precisas y detalladas sobre los documentos que se han comparado.

INSTRUCCIONES IMPORTANTES:
1. Responde ÚNICAMENTE basándote en la información proporcionada en los documentos
2. Sé preciso y específico, citando números de artículos, secciones o capítulos cuando sea posible
3. Si la información no está en los documentos, di claramente que no tienes esa información
4. Identifica diferencias específicas entre los documentos cuando se pregunten
5. Usa un lenguaje profesional pero claro
6. Estructura tus respuestas de manera clara y organizada
7. Si se pregunta sobre cambios, explica qué cambió, dónde cambió y el impacto potencial
8. Sé conciso pero completo en tus respuestas

Responde siempre en español y de manera profesional."""

    def clear_history(self):
        """Limpia el historial de conversación"""
        self.conversation_history = []





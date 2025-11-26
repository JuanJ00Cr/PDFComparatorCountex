"""
Módulo para generar explicaciones de diferencias usando IA
"""
import os
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class AIExplainer:
    """Clase para generar explicaciones inteligentes de diferencias usando IA"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY no está configurada en el archivo .env")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Puedes cambiar a gpt-4 si prefieres
    
    def explain_differences(self, comparison_result: Dict) -> str:
        """
        Genera una explicación detallada de las diferencias entre documentos
        
        Args:
            comparison_result: Resultado de la comparación de documentos
            
        Returns:
            Explicación generada por IA
        """
        # Preparar contexto para la IA
        context = self._prepare_context(comparison_result)
        
        # Crear prompt para la IA
        prompt = self._create_prompt(context, comparison_result)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de documentos legales y reglamentarios. "
                                 "Tu tarea es explicar de manera clara y profesional las diferencias entre "
                                 "documentos, especialmente cambios en reglamentaciones y normas. "
                                 "Identifica artículos modificados, agregados o eliminados, y explica "
                                 "el impacto de estos cambios."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error al generar explicación: {str(e)}"
    
    def _prepare_context(self, comparison_result: Dict) -> str:
        """
        Prepara el contexto de las diferencias para la IA
        
        Args:
            comparison_result: Resultado de la comparación
            
        Returns:
            Contexto formateado como string
        """
        context_parts = []
        
        # Información general
        stats = comparison_result['statistics']
        context_parts.append(f"Estadísticas de comparación:")
        context_parts.append(f"- Total de diferencias: {stats['total_differences']}")
        context_parts.append(f"- Secciones agregadas: {stats['added_sections']}")
        context_parts.append(f"- Secciones eliminadas: {stats['deleted_sections']}")
        context_parts.append(f"- Secciones modificadas: {stats['modified_sections']}")
        context_parts.append(f"- Similitud: {comparison_result['similarity_ratio']:.2%}")
        context_parts.append("")
        
        # Diferencias detalladas (limitadas para no exceder tokens)
        context_parts.append("Diferencias encontradas:")
        differences = comparison_result['differences'][:20]  # Limitar a 20 diferencias
        
        for i, diff in enumerate(differences, 1):
            context_parts.append(f"\n--- Diferencia {i} ({diff['type']}) ---")
            
            if diff['type'] == 'added':
                context_parts.append("Líneas agregadas:")
                for line in diff['lines'][:5]:  # Limitar líneas
                    context_parts.append(f"  + {line}")
            
            elif diff['type'] == 'deleted':
                context_parts.append("Líneas eliminadas:")
                for line in diff['lines'][:5]:
                    context_parts.append(f"  - {line}")
            
            elif diff['type'] == 'modified':
                context_parts.append("Líneas modificadas:")
                context_parts.append("Antes:")
                for line in diff['old_lines'][:3]:
                    context_parts.append(f"  - {line}")
                context_parts.append("Después:")
                for line in diff['new_lines'][:3]:
                    context_parts.append(f"  + {line}")
            
            # Contexto
            if diff.get('context'):
                ctx = diff['context']
                if ctx.get('before_doc1'):
                    context_parts.append("Contexto anterior:")
                    for line in ctx['before_doc1'][-2:]:
                        context_parts.append(f"  {line}")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, context: str, comparison_result: Dict) -> str:
        """
        Crea el prompt para la IA
        
        Args:
            context: Contexto de las diferencias
            comparison_result: Resultado completo de la comparación
            
        Returns:
            Prompt formateado
        """
        prompt = f"""Analiza las siguientes diferencias entre dos documentos (probablemente reglamentaciones o normas) 
y proporciona una explicación detallada y profesional.

{context}

Por favor, proporciona:
1. Un resumen ejecutivo de los cambios principales
2. Identificación de artículos, capítulos o secciones afectadas
3. Explicación del impacto de cada tipo de cambio (agregados, eliminados, modificados)
4. Recomendaciones sobre qué aspectos requieren atención especial
5. Identificación de posibles inconsistencias o áreas que necesitan revisión

Formatea la respuesta de manera clara y estructurada, usando secciones y viñetas cuando sea apropiado.
"""
        return prompt
    
    def explain_specific_difference(self, difference: Dict, 
                                   comparison_result: Dict) -> str:
        """
        Genera una explicación detallada de una diferencia específica
        
        Args:
            difference: Una diferencia específica
            comparison_result: Resultado completo de la comparación
            
        Returns:
            Explicación de la diferencia específica
        """
        prompt = f"""Analiza esta diferencia específica entre dos documentos reglamentarios:

Tipo de cambio: {difference['type']}

"""
        
        if difference['type'] == 'added':
            prompt += "Contenido agregado:\n"
            for line in difference['lines']:
                prompt += f"  + {line}\n"
        
        elif difference['type'] == 'deleted':
            prompt += "Contenido eliminado:\n"
            for line in difference['lines']:
                prompt += f"  - {line}\n"
        
        elif difference['type'] == 'modified':
            prompt += "Contenido modificado:\n"
            prompt += "Versión anterior:\n"
            for line in difference['old_lines']:
                prompt += f"  - {line}\n"
            prompt += "Versión nueva:\n"
            for line in difference['new_lines']:
                prompt += f"  + {line}\n"
        
        if difference.get('context'):
            ctx = difference['context']
            prompt += "\nContexto:\n"
            if ctx.get('before_doc1'):
                prompt += "Líneas anteriores:\n"
                for line in ctx['before_doc1'][-3:]:
                    prompt += f"  {line}\n"
        
        prompt += "\nExplica el significado y el impacto de este cambio específico en el contexto de una reglamentación o norma."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en análisis de documentos legales y reglamentarios."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error al generar explicación: {str(e)}"


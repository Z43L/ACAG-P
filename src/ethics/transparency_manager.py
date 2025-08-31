from typing import Dict, Any, List
import json

class TransparencyManager:
    """Gestiona la transparencia y explicabilidad de las decisiones del sistema"""
    
    def __init__(self):
        self.decision_log = []
        self.explanation_templates = {
            'knowledge_based': "Basado en el conocimiento verificado de {sources}",
            'inference': "Inferido mediante análisis de patrones en {context}",
            'external_model': "Generado por modelo externo {model_name} con confianza {confidence}"
        }
        
    def log_decision(self, decision_id: str, inputs: Dict, outputs: Dict, 
                   rationale: str, sources: List[str]) -> bool:
        """Registra una decisión del sistema con su explicación completa"""
        log_entry = {
            'decision_id': decision_id,
            'timestamp': datetime.now().isoformat(),
            'inputs': inputs,
            'outputs': outputs,
            'rationale': rationale,
            'sources': sources,
            'metadata': {
                'version': '1.0',
                'system_state': 'operational'
            }
        }
        
        self.decision_log.append(log_entry)
        return True
        
    def generate_explanation(self, response: str, context: Dict) -> str:
        """Genera una explicación comprensible para una respuesta dada"""
        explanation_parts = []
        
        # Añadir fuentes de conocimiento si están disponibles
        if context.get('knowledge_sources'):
            sources = context['knowledge_sources']
            explanation_parts.append(
                self.explanation_templates['knowledge_based'].format(
                    sources=", ".join(sources[:3])
                )
            )
        
        # Añadir información del modelo si es relevante
        if context.get('model_used'):
            model_info = context['model_used']
            explanation_parts.append(
                self.explanation_templates['external_model'].format(
                    model_name=model_info['name'],
                    confidence=f"{model_info['confidence']*100:.1f}%"
                )
            )
        
        return " | ".join(explanation_parts) if explanation_parts else \
               "Basado en el análisis integral del conocimiento disponible"
    
    def get_decision_history(self, user_id: str = None, 
                           limit: int = 100) -> List[Dict]:
        """Obtiene el historial de decisiones, opcionalmente filtrado por usuario"""
        if user_id:
            return [log for log in self.decision_log 
                   if log['inputs'].get('user_id') == user_id][-limit:]
        return self.decision_log[-limit:]
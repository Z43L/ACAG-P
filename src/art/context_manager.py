from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

@dataclass
class ConversationContext:
    """Estructura para gestionar el contexto de conversación"""
    user_id: str
    conversation_history: List[Dict[str, str]]
    user_preferences: Dict[str, Any]
    temporal_context: Dict[str, Any]
    knowledge_context: Dict[str, Any]

class ContextManager:
    """Gestiona el contexto para las consultas del ART"""
    
    def __init__(self, ncd_client, max_history_length: int = 10):
        self.ncd_client = ncd_client
        self.max_history_length = max_history_length
        self.conversation_contexts: Dict[str, ConversationContext] = {}
        self.logger = logging.getLogger(__name__)
        
    def get_context(self, user_id: str, query: str) -> ConversationContext:
        """Obtiene contexto completo para una consulta"""
        # Obtener o crear contexto de conversación
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(
                user_id=user_id,
                conversation_history=[],
                user_preferences={},
                temporal_context={},
                knowledge_context={}
            )
            
        context = self.conversation_contexts[user_id]
        
        # Actualizar contexto con información relevante
        context.knowledge_context = self._get_knowledge_context(query)
        context.temporal_context = self._get_temporal_context()
        
        return context
        
    def update_conversation_history(self, user_id: str, query: str, response: str) -> None:
        """Actualiza el historial de conversación"""
        if user_id not in self.conversation_contexts:
            return
            
        context = self.conversation_contexts[user_id]
        context.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response
        })
        
        # Mantener límite de historial
        if len(context.conversation_history) > self.max_history_length:
            context.conversation_history = context.conversation_history[-self.max_history_length:]
            
    def _get_knowledge_context(self, query: str) -> Dict[str, Any]:
        """Obtiene conocimiento relevante del NCD"""
        try:
            # Búsqueda semántica en Pinecone
            semantic_results = self.ncd_client.semantic_search(query, top_k=3)
            
            # Extraer entidades para búsqueda en grafo
            entities = self._extract_entities(query)
            graph_context = {}
            
            for entity in entities:
                entity_data = self.ncd_client.find_entities('Entity', {'name': entity})
                if entity_data:
                    graph_context[entity] = entity_data[0]
                    
            return {
                'semantic_results': semantic_results,
                'graph_context': graph_context,
                'entities_identified': entities
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo contexto de conocimiento: {str(e)}")
            return {}
            
    def _extract_entities(self, text: str) -> List[str]:
        """Extrae entidades potenciales del texto (simplificado)"""
        # En implementación real usaríamos NER del MPE
        import re
        # Palabras con mayúscula inicial (aproximación simple)
        return re.findall(r'\b[A-Z][a-z]+\b', text)
        
    def _get_temporal_context(self) -> Dict[str, Any]:
        """Obtiene contexto temporal"""
        now = datetime.now()
        return {
            'timestamp': now.isoformat(),
            'time_of_day': now.strftime('%H:%M'),
            'day_of_week': now.strftime('%A'),
            'season': self._get_season(now)
        }
        
    def _get_season(self, date: datetime) -> str:
        """Determina la estación del año"""
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
            
    def clear_context(self, user_id: str) -> bool:
        """Limpia el contexto de un usuario"""
        if user_id in self.conversation_contexts:
            del self.conversation_contexts[user_id]
            return True
        return False
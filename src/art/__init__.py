"""
Agente de Razonamiento y Tareas (ART) - ACAG-P
Sistema central de procesamiento de consultas y generación de respuestas
"""

from typing import Dict, Any, Optional
import logging
from .context_manager import ContextManager
from .model_router import ModelRouter, QueryComplexity, ModelType
from .knowledge_validator import KnowledgeValidator

class ReasoningTaskAgent:
    """Clase principal del Agente de Razonamiento y Tareas"""
    
    def __init__(self, ncd_client, config: Dict[str, Any]):
        self.ncd_client = ncd_client
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.context_manager = ContextManager(ncd_client)
        self.model_router = ModelRouter(
            local_model_path=config.get('local_model_path', './models/local'),
            openrouter_api_key=config.get('openrouter_api_key')
        )
        self.validator = KnowledgeValidator(ncd_client)
        
        self.initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el ART"""
        try:
            # Verificar dependencias
            if not self.ncd_client:
                raise ValueError("NCD client no proporcionado")
                
            self.initialized = True
            self.logger.info("ART inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando ART: {str(e)}")
            self.initialized = False
            return False
            
    def process_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """
        Procesa una consulta completa y devuelve respuesta
        
        Returns:
            Dict con respuesta y metadatos de procesamiento
        """
        if not self.initialized:
            raise RuntimeError("ART no inicializado")
            
        try:
            # Obtener contexto
            context = self.context_manager.get_context(user_id, query)
            
            # Procesar con router de modelos
            raw_response = self.model_router.process_query(query, context)
            
            # Validar contra conocimiento
            validation_result = self.validator.validate_response(raw_response, context)
            
            # Actualizar historial de conversación
            self.context_manager.update_conversation_history(
                user_id, query, validation_result['enhanced_response']
            )
            
            return {
                'response': validation_result['enhanced_response'],
                'metadata': {
                    'user_id': user_id,
                    'query': query,
                    'processing_time': None,  # Se calcularía en implementación real
                    'model_used': self._get_model_used(context),
                    'validation_result': validation_result['validation_result'],
                    'context_used': {
                        'history_length': len(context.conversation_history),
                        'knowledge_sources': len(context.knowledge_context.get('semantic_results', []))
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando consulta: {str(e)}")
            return self._generate_error_response(query, str(e))
            
    def _get_model_used(self, context: Any) -> str:
        """Determina qué modelo se usó (simplificado)"""
        # En implementación real, el router debería trackear esto
        return "hybrid"
        
    def _generate_error_response(self, query: str, error: str) -> Dict[str, Any]:
        """Genera una respuesta de error apropiada"""
        return {
            'response': f"Lo siento, hubo un error procesando tu consulta sobre '{query}'. Por favor, intenta de nuevo.",
            'metadata': {
                'error': error,
                'response_type': 'error'
            }
        }
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de performance del ART"""
        return {
            'total_queries_processed': 0,  # Se implementaría tracking real
            'average_response_time': 0,
            'success_rate': 1.0,
            'cost_metrics': self.model_router.cost_tracker.get_cost_report()
        }
        
    def clear_user_context(self, user_id: str) -> bool:
        """Limpia el contexto de un usuario específico"""
        return self.context_manager.clear_context(user_id)
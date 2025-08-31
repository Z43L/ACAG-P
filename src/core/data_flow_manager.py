from typing import Dict, Any
from datetime import datetime
import logging

class DataFlowManager:
    """Gestiona los flujos de datos principales del sistema ACAG-P"""
    
    def __init__(self, integration_manager):
        self.integration = integration_manager
        self.logger = logging.getLogger(__name__)
        
    def start_ingestion_flow(self, source_type: str, parameters: Dict[str, Any]) -> str:
        """Inicia el flujo de ingesta de datos desde una fuente"""
        flow_id = f"flow_ingest_{datetime.now().timestamp()}"
        
        message = {
            'type': 'ingestion_start',
            'flow_id': flow_id,
            'source_type': source_type,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
        
        self.integration.publish_message('data_ingestion', message)
        return flow_id
        
    def start_learning_cycle(self, trigger: str = 'scheduled') -> str:
        """Inicia un ciclo de aprendizaje automático"""
        cycle_id = f"cycle_learn_{datetime.now().timestamp()}"
        
        message = {
            'type': 'learning_cycle_start',
            'cycle_id': cycle_id,
            'trigger': trigger,
            'timestamp': datetime.now().isoformat()
        }
        
        self.integration.publish_message('learning_cycles', message)
        return cycle_id
        
    def process_user_query(self, user_id: str, query: str, context: Dict[str, Any] = None) -> str:
        """Procesa una consulta de usuario a través del flujo completo"""
        session_id = f"session_{user_id}_{datetime.now().timestamp()}"
        
        message = {
            'type': 'user_query',
            'session_id': session_id,
            'user_id': user_id,
            'query': query,
            'context': context or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.integration.publish_message('reasoning_tasks', message)
        return session_id
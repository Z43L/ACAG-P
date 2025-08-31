from typing import Dict, Any, List
import json
import redis
from datetime import datetime
import logging

class IntegrationManager:
    """Gestiona la comunicación y coordinación entre todos los módulos de ACAG-P"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.message_queues = {
            'data_ingestion': 'acag:queue:ingestion',
            'knowledge_processing': 'acag:queue:processing',
            'reasoning_tasks': 'acag:queue:reasoning',
            'learning_cycles': 'acag:queue:learning',
            'interpersonal_events': 'acag:queue:interpersonal'
        }
        self.logger = logging.getLogger(__name__)
        
    def publish_message(self, queue_name: str, message: Dict[str, Any]) -> bool:
        """Publica un mensaje en la cola especificada"""
        if queue_name not in self.message_queues:
            raise ValueError(f"Cola no válida: {queue_name}. Opciones: {list(self.message_queues.keys())}")
        
        try:
            message_with_metadata = {
                'payload': message,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'message_id': f"msg_{datetime.now().timestamp()}",
                    'source_module': message.get('source', 'unknown')
                }
            }
            
            serialized = json.dumps(message_with_metadata)
            self.redis_client.rpush(self.message_queues[queue_name], serialized)
            self.logger.debug(f"Mensaje publicado en {queue_name}: {message['type']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error publicando mensaje: {str(e)}")
            return False
            
    def subscribe_to_queue(self, queue_name: str, callback: callable) -> None:
        """Suscribe un callback a una cola específica para procesamiento continuo"""
        if queue_name not in self.message_queues:
            raise ValueError(f"Cola no válida: {queue_name}")
            
        def queue_listener():
            while True:
                try:
                    message = self.redis_client.blpop(self.message_queues[queue_name], timeout=30)
                    if message:
                        _, serialized = message
                        message_data = json.loads(serialized)
                        callback(message_data)
                        
                except Exception as e:
                    self.logger.error(f"Error en listener de {queue_name}: {str(e)}")
                    time.sleep(5)
        
        import threading
        thread = threading.Thread(target=queue_listener, daemon=True)
        thread.start()
        self.logger.info(f"Suscrito a cola {queue_name}")
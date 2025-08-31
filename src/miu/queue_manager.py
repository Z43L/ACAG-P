import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime
import threading
import time

class QueueManager:
    """Gestiona colas de procesamiento para el MIU"""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        self.queues = {
            'high_priority': 'miu:queue:high',
            'normal': 'miu:queue:normal', 
            'low_priority': 'miu:queue:low'
        }
        self.processing_lock = threading.Lock()
        
    def enqueue(self, data: Dict[str, Any], priority: str = 'normal') -> str:
        """Añade datos a la cola especificada"""
        if priority not in self.queues:
            raise ValueError(f"Priority must be one of {list(self.queues.keys())}")
            
        queue_name = self.queues[priority]
        
        # Añadir metadatos de enqueue
        enriched_data = {
            'data': data,
            'metadata': {
                'enqueued_at': datetime.now().isoformat(),
                'priority': priority,
                'attempts': 0
            }
        }
        
        try:
            serialized = json.dumps(enriched_data)
            self.redis_client.rpush(queue_name, serialized)
            return f"Data enqueued to {queue_name}"
        except Exception as e:
            raise Exception(f"Failed to enqueue data: {str(e)}")
            
    def dequeue(self, priority: str = 'normal') -> Optional[Dict[str, Any]]:
        """Extrae datos de la cola especificada"""
        if priority not in self.queues:
            raise ValueError(f"Priority must be one of {list(self.queues.keys())}")
            
        queue_name = self.queues[priority]
        
        try:
            with self.processing_lock:
                serialized = self.redis_client.lpop(queue_name)
                if serialized:
                    data = json.loads(serialized)
                    data['metadata']['dequeued_at'] = datetime.now().isoformat()
                    return data
            return None
        except Exception as e:
            raise Exception(f"Failed to dequeue data: {str(e)}")
            
    def get_queue_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de todas las colas"""
        stats = {}
        for priority, queue_name in self.queues.items():
            length = self.redis_client.llen(queue_name)
            stats[priority] = {
                'queue_name': queue_name,
                'length': length,
                'memory_usage': self._get_queue_memory_usage(queue_name)
            }
        return stats
        
    def _get_queue_memory_usage(self, queue_name: str) -> int:
        """Estima el uso de memoria de una cola"""
        items = self.redis_client.lrange(queue_name, 0, -1)
        total_size = sum(len(item.encode('utf-8')) for item in items)
        return total_size
        
    def start_processing_worker(self, callback: callable, 
                              worker_id: str = "worker_1") -> None:
        """Inicia un worker que procesa elementos de la cola"""
        def worker_loop():
            while True:
                try:
                    # Intentar todas las colas en orden de prioridad
                    for priority in ['high_priority', 'normal', 'low_priority']:
                        item = self.dequeue(priority)
                        if item:
                            try:
                                callback(item['data'])
                                # Marcar como procesado exitosamente
                                self._mark_processed(item)
                            except Exception as e:
                                # Reintentar o mover a dead letter queue
                                self._handle_processing_error(item, str(e))
                                break
                    
                    time.sleep(1)  # Evitar busy waiting
                    
                except Exception as e:
                    print(f"Worker error: {str(e)}")
                    time.sleep(5)
                    
        worker_thread = threading.Thread(target=worker_loop, daemon=True)
        worker_thread.start()
        print(f"Started processing worker {worker_id}")
        
    def _mark_processed(self, item: Dict[str, Any]) -> None:
        """Marca un ítem como procesado exitosamente"""
        # Implementar logging o tracking de procesamiento exitoso
        pass
        
    def _handle_processing_error(self, item: Dict[str, Any], error: str) -> None:
        """Maneja errores de procesamiento"""
        attempts = item['metadata'].get('attempts', 0) + 1
        
        if attempts >= 3:
            # Mover a dead letter queue después de 3 intentos
            self._move_to_dlq(item, error)
        else:
            # Reintentar
            item['metadata']['attempts'] = attempts
            item['metadata']['last_error'] = error
            self.enqueue(item['data'], item['metadata']['priority'])
            
    def _move_to_dlq(self, item: Dict[str, Any], error: str) -> None:
        """Mueve un ítem a la dead letter queue"""
        dlqitem = {
            'original_data': item['data'],
            'error_info': {
                'error': error,
                'attempts': item['metadata']['attempts'],
                'first_failed': item['metadata'].get('enqueued_at'),
                'last_failed': datetime.now().isoformat()
            }
        }
        
        self.redis_client.rpush('miu:queue:dead_letter', json.dumps(dlq_item))
from typing import Dict, List, Any
from datetime import datetime
import logging

class SyncManager:
    """Gestiona la sincronización entre la base de grafos y la vectorial"""
    
    def __init__(self, graph_db, vector_db):
        self.graph_db = graph_db
        self.vector_db = vector_db
        self.sync_interval = 300  # 5 minutos
        
    def full_sync(self) -> Dict[str, Any]:
        """Sincronización completa entre ambas bases de datos"""
        sync_report = {
            'start_time': datetime.now().isoformat(),
            'entities_processed': 0,
            'vectors_processed': 0,
            'errors': []
        }
        
        try:
            # Obtener todas las entidades del grafo
            entities = self.graph_db.find_entities()
            
            for entity in entities:
                try:
                    # Convertir entidad a formato vectorial
                    vector_data = self._entity_to_vector(entity['n'])
                    
                    # Insertar en base vectorial
                    self.vector_db.upsert_vectors([vector_data])
                    
                    sync_report['entities_processed'] += 1
                    sync_report['vectors_processed'] += 1
                    
                except Exception as e:
                    sync_report['errors'].append(f"Entity {entity['n'].get('id')}: {str(e)}")
                    
        except Exception as e:
            sync_report['errors'].append(f"Sync failed: {str(e)}")
            
        sync_report['end_time'] = datetime.now().isoformat()
        sync_report['success'] = len(sync_report['errors']) == 0
        
        return sync_report
        
    def _entity_to_vector(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Convierte una entidad de grafo a formato vectorial"""
        # Extraer texto para embedding (depende de la estructura de la entidad)
        text_parts = []
        
        if 'text' in entity:
            text_parts.append(entity['text'])
        if 'name' in entity:
            text_parts.append(entity['name'])
        if 'description' in entity:
            text_parts.append(entity['description'])
            
        text = ' '.join(text_parts)
        
        # Generar embedding (en producción usaríamos el MPE)
        # Esto es un placeholder - en implementación real se usaría el modelo de embeddings
        embedding = self._generate_dummy_embedding(text)
        
        return {
            'id': entity.get('id', ''),
            'embeddings': embedding,
            'metadata': {
                'type': entity.get('type', 'Entity'),
                'source': 'graph_db',
                'text': text,
                **{k: v for k, v in entity.items() 
                  if k not in ['id', 'text', 'name', 'description']}
            }
        }
        
    def _generate_dummy_embedding(self, text: str) -> List[float]:
        """Genera un embedding dummy para demostración"""
        # En producción, esto se reemplazaría con el modelo real de embeddings
        return [0.1] * 384  # Dimensión típica para all-MiniLM-L6-v2
        
    def start_continuous_sync(self) -> None:
        """Inicia la sincronización continua en segundo plano"""
        import threading
        import time
        
        def sync_loop():
            while True:
                try:
                    self.full_sync()
                    time.sleep(self.sync_interval)
                except Exception as e:
                    logging.error(f"Continuous sync failed: {str(e)}")
                    time.sleep(60)  # Esperar antes de reintentar
                    
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
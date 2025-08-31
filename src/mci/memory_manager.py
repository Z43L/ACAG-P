from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from enum import Enum
import os

class MemoryType(Enum):
    """Tipos de memoria manejados por el sistema"""
    FACTUAL = "factual"          # Hechos sobre el usuario
    PREFERENCE = "preference"    # Preferencias del usuario
    EXPERIENTIAL = "experiential" # Experiencias compartidas
    EMOTIONAL = "emotional"      # Estados emocionales

@dataclass
class MemoryItem:
    """Elemento individual de memoria"""
    memory_id: str
    user_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    importance: float  # 0.0 to 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int

class MemoryManager:
    """Gestiona el sistema de memoria a corto y largo plazo"""
    
    def __init__(self, ncd_client, storage_path: str = "./data/memories"):
        self.ncd_client = ncd_client
        self.storage_path = storage_path
        self.short_term_memory: Dict[str, List[MemoryItem]] = {}
        self.logger = logging.getLogger(__name__)
        
        self._load_memories()
        
    def _load_memories(self) -> None:
        """Carga memorias desde almacenamiento persistente"""
        try:
            memories_file = f"{self.storage_path}/long_term_memories.json"
            if os.path.exists(memories_file):
                with open(memories_file, 'r') as f:
                    memories_data = json.load(f)
                    
                # En implementación real, cargaríamos las memorias
                self.logger.info(f"Loaded {len(memories_data)} long-term memories")
                
        except Exception as e:
            self.logger.error(f"Error loading memories: {str(e)}")
            
    def add_memory(self, user_id: str, memory_type: MemoryType, 
                  content: Dict[str, Any], importance: float = 0.5) -> str:
        """Añade una nueva memoria al sistema"""
        memory_id = f"memory_{datetime.now().timestamp()}"
        now = datetime.now()
        
        memory_item = MemoryItem(
            memory_id=memory_id,
            user_id=user_id,
            memory_type=memory_type,
            content=content,
            importance=importance,
            created_at=now,
            last_accessed=now,
            access_count=1
        )
        
        # Almacenar en memoria a corto plazo
        if user_id not in self.short_term_memory:
            self.short_term_memory[user_id] = []
        self.short_term_memory[user_id].append(memory_item)
        
        # Si es importante, almacenar en largo plazo (NCD)
        if importance > 0.7:
            self._store_in_long_term_memory(memory_item)
            
        return memory_id
        
    def _store_in_long_term_memory(self, memory_item: MemoryItem) -> None:
        """Almacena una memoria importante en el NCD"""
        try:
            # Convertir a formato de grafo de conocimiento
            memory_data = {
                'type': 'Memory',
                'user_id': memory_item.user_id,
                'memory_type': memory_item.memory_type.value,
                'content': memory_item.content,
                'importance': memory_item.importance,
                'created_at': memory_item.created_at.isoformat()
            }
            
            # Almacenar en NCD
            self.ncd_client.process_data({
                'graph_data': {
                    'nodes': [{
                        'id': memory_item.memory_id,
                        'labels': ['Memory', memory_item.memory_type.value],
                        **memory_data
                    }],
                    'relationships': [{
                        'source': memory_item.user_id,
                        'target': memory_item.memory_id,
                        'type': 'HAS_MEMORY'
                    }]
                }
            }, 'structured')
            
        except Exception as e:
            self.logger.error(f"Error storing memory in NCD: {str(e)}")
            
    def get_relevant_memories(self, user_id: str, context: Dict[str, Any], 
                             max_memories: int = 5) -> List[MemoryItem]:
        """Recupera memorias relevantes para el contexto actual"""
        relevant_memories = []
        
        # Buscar en memoria a corto plazo primero
        if user_id in self.short_term_memory:
            for memory in self.short_term_memory[user_id]:
                if self._is_memory_relevant(memory, context):
                    relevant_memories.append(memory)
                    memory.last_accessed = datetime.now()
                    memory.access_count += 1
        
        # Si no hay suficientes, buscar en largo plazo
        if len(relevant_memories) < max_memories:
            long_term_memories = self._search_long_term_memories(user_id, context)
            relevant_memories.extend(long_term_memories[:max_memories - len(relevant_memories)])
            
        # Ordenar por relevancia (importance + recency)
        relevant_memories.sort(key=lambda m: (
            m.importance * 0.7 + 
            self._calculate_recency_score(m.last_accessed) * 0.3
        ), reverse=True)
        
        return relevant_memories[:max_memories]
        
    def _is_memory_relevant(self, memory: MemoryItem, context: Dict[str, Any]) -> bool:
        """Determina si una memoria es relevante para el contexto"""
        # Lógica simple de relevancia - en producción sería más compleja
        context_topics = context.get('topics', [])
        memory_content = str(memory.content).lower()
        
        for topic in context_topics:
            if topic.lower() in memory_content:
                return True
                
        return False
        
    def _search_long_term_memories(self, user_id: str, context: Dict[str, Any]) -> List[MemoryItem]:
        """Busca memorias en el almacenamiento a largo plazo"""
        # En implementación real, haríamos queries al NCD
        return []  # Placeholder
        
    def _calculate_recency_score(self, last_accessed: datetime) -> float:
        """Calcula un score de recencia basado en el último acceso"""
        hours_since_access = (datetime.now() - last_accessed).total_seconds() / 3600
        return max(0, 1 - (hours_since_access / 720))  # Decae en 30 días
        
    def cleanup_short_term_memory(self) -> None:
        """Limpia la memoria a corto plazo de elementos antiguos"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for user_id in list(self.short_term_memory.keys()):
            self.short_term_memory[user_id] = [
                memory for memory in self.short_term_memory[user_id]
                if memory.last_accessed > cutoff_time or memory.importance > 0.8
            ]
            
            # Eliminar lista vacía
            if not self.short_term_memory[user_id]:
                del self.short_term_memory[user_id]
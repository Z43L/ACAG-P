from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class UnifiedQueryClient:
    """Cliente unificado para consultas en el Núcleo de Conocimiento Dual"""
    
    def __init__(self, neo4j_manager, pinecone_manager):
        self.neo4j = neo4j_manager
        self.pinecone = pinecone_manager
        self.logger = logging.getLogger(__name__)
        
    def execute_cypher(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """Ejecuta consultas Cypher en Neo4j"""
        return self.neo4j.execute_query(query, parameters or {})
        
    def semantic_search(self, query: str, top_k: int = 5, 
                       filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Realiza búsqueda semántica en Pinecone"""
        return self.pinecone.semantic_search(query, top_k, filters)
        
    def hybrid_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Búsqueda híbrida que combina resultados semánticos y estructurales
        
        Args:
            query: Consulta de búsqueda
            top_k: Número máximo de resultados
            
        Returns:
            Resultados enriquecidos con contexto estructural
        """
        try:
            # Primero búsqueda semántica
            semantic_results = self.semantic_search(query, top_k * 2)
            
            # Enriquecer con datos del grafo
            enriched_results = []
            for result in semantic_results:
                # Extraer entidades del resultado semántico
                entity_ids = self._extract_entity_ids(result)
                
                # Obtener contexto del grafo
                graph_context = self._get_graph_context(entity_ids)
                
                enriched_results.append({
                    **result,
                    "graph_context": graph_context,
                    "enriched_at": datetime.now().isoformat()
                })
                
                if len(enriched_results) >= top_k:
                    break
                    
            return enriched_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda híbrida: {str(e)}")
            raise
            
    def _extract_entity_ids(self, semantic_result: Dict[str, Any]) -> List[str]:
        """Extrae IDs de entidades de un resultado semántico"""
        metadata = semantic_result.get("metadata", {})
        entity_ids = []
        
        # Extraer IDs de diferentes campos de metadatos
        for field in ["entity_id", "source_id", "related_entities"]:
            if field in metadata:
                ids = metadata[field]
                if isinstance(ids, str):
                    entity_ids.append(ids)
                elif isinstance(ids, list):
                    entity_ids.extend(ids)
                    
        return list(set(entity_ids))  # Devolver únicos
        
    def _get_graph_context(self, entity_ids: List[str]) -> Dict[str, Any]:
        """Obtiene contexto del grafo para las entidades dadas"""
        if not entity_ids:
            return {}
            
        try:
            # Consultar relaciones y propiedades de las entidades
            query = """
            UNWIND $entity_ids AS entity_id
            MATCH (e {id: entity_id})
            OPTIONAL MATCH (e)-[r]-(related)
            WHERE related.id IS NOT NULL
            RETURN e.id as entity_id, 
                   properties(e) as entity_properties,
                   collect(DISTINCT {type: type(r), 
                                   target: related.id, 
                                   properties: properties(r)}) as relationships
            """
            
            results = self.execute_cypher(query, {"entity_ids": entity_ids})
            return {item["entity_id"]: item for item in results}
            
        except Exception as e:
            self.logger.warning(f"Error obteniendo contexto del grafo: {str(e)}")
            return {}
            
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas combinadas del sistema NCD"""
        try:
            neo4j_stats = self.neo4j.execute_query(
                "CALL db.labels() YIELD label RETURN count(*) as node_count"
            )
            
            pinecone_stats = self.pinecone.get_index_stats()
            
            return {
                "neo4j": {
                    "node_count": neo4j_stats[0]["node_count"] if neo4j_stats else 0,
                    "database": self.neo4j.database
                },
                "pinecone": {
                    "vector_count": pinecone_stats.get("total_vector_count", 0),
                    "index_name": self.pinecone.index_name
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estadísticas del sistema: {str(e)}")
            return {"error": str(e)}
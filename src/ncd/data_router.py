from typing import Dict, List, Any, Optional
from enum import Enum
import logging
from datetime import datetime

class DataType(Enum):
    """Tipos de datos para el routing en NCD"""
    STRUCTURED = "structured"  # Datos para grafo (entidades, relaciones)
    SEMANTIC = "semantic"      # Datos para vectores (texto para embeddings)
    HYBRID = "hybrid"          # Datos para ambos sistemas
    METADATA = "metadata"      # Metadatos del sistema

class DataRouter:
    """Router inteligente para distribuir datos entre Neo4j y Pinecone"""
    
    def __init__(self, neo4j_manager, pinecone_manager):
        self.neo4j = neo4j_manager
        self.pinecone = pinecone_manager
        self.logger = logging.getLogger(__name__)
        
    def route_data(self, data: Dict[str, Any], data_type: DataType) -> Dict[str, Any]:
        """
        Enruta datos al almacenamiento apropiado según el tipo
        
        Args:
            data: Datos a almacenar
            data_type: Tipo de dato (STRUCTURED, SEMANTIC, HYBRID)
            
        Returns:
            Resultados del routing
        """
        results = {
            "neo4j_success": False,
            "pinecone_success": False,
            "errors": []
        }
        
        try:
            # Routing basado en el tipo de dato
            if data_type in [DataType.STRUCTURED, DataType.HYBRID]:
                results.update(self._route_to_neo4j(data))
                
            if data_type in [DataType.SEMANTIC, DataType.HYBRID]:
                results.update(self._route_to_pinecone(data))
                
            return results
            
        except Exception as e:
            error_msg = f"Error en routing de datos: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            return results
            
    def _route_to_neo4j(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta datos estructurados a Neo4j"""
        result = {"neo4j_success": False}
        
        try:
            graph_data = data.get("graph_data", {})
            if graph_data:
                stats = self.neo4j.import_graph_data(graph_data)
                result["neo4j_success"] = stats["errors"] == 0
                result["neo4j_stats"] = stats
                self.logger.info(f"Datos enrutados a Neo4j: {stats}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error routing a Neo4j: {str(e)}")
            result["neo4j_error"] = str(e)
            return result
            
    def _route_to_pinecone(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Enruta datos semánticos a Pinecone"""
        result = {"pinecone_success": False}
        
        try:
            text_content = data.get("processed_text", "")
            metadata = data.get("metadata", {})
            
            if text_content:
                # Generar embeddings
                embeddings = self.pinecone.generate_embeddings(text_content)
                
                # Crear vector con ID único
                vector_id = f"doc_{datetime.now().timestamp()}"
                vector_data = {
                    "id": vector_id,
                    "embeddings": embeddings,
                    "metadata": {
                        **metadata,
                        "text_length": len(text_content),
                        "processed_at": datetime.now().isoformat()
                    }
                }
                
                # Insertar en Pinecone
                upsert_result = self.pinecone.upsert_vectors([vector_data])
                result["pinecone_success"] = True
                result["pinecone_stats"] = upsert_result
                self.logger.info(f"Datos enrutados a Pinecone: {upsert_result}")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error routing a Pinecone: {str(e)}")
            result["pinecone_error"] = str(e)
            return result
            
    def determine_data_type(self, data: Dict[str, Any]) -> DataType:
        """
        Determina automáticamente el tipo de dato para routing
        
        Args:
            data: Datos a analizar
            
        Returns:
            Tipo de dato determinado
        """
        has_graph_data = "graph_data" in data and data["graph_data"]
        has_text_content = "processed_text" in data and data["processed_text"]
        
        if has_graph_data and has_text_content:
            return DataType.HYBRID
        elif has_graph_data:
            return DataType.STRUCTURED
        elif has_text_content:
            return DataType.SEMANTIC
        else:
            return DataType.METADATA
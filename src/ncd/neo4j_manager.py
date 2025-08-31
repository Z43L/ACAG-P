from neo4j import GraphDatabase, basic_auth
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class Neo4jManager:
    """Gestor de conexiones y operaciones con Neo4j para ACAG-P"""
    
    def __init__(self, uri: str, user: str, password: str, database: str = "acag_knowledge"):
        self.driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
        self.database = database
        self.logger = logging.getLogger(__name__)
        self._verify_connection()
        
    def _verify_connection(self) -> bool:
        """Verifica la conexión con la base de datos"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 AS test")
                return result.single()["test"] == 1
        except Exception as e:
            self.logger.error(f"Conexión fallida con Neo4j: {str(e)}")
            raise ConnectionError(f"No se pudo conectar a Neo4j: {str(e)}")
            
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """Ejecuta una consulta Cypher y devuelve resultados"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            self.logger.error(f"Error ejecutando query: {query[:100]}... - {str(e)}")
            raise
            
    def create_constraints(self) -> None:
        """Crea constraints y índices para optimizar el rendimiento"""
        constraints_queries = [
            "CREATE CONSTRAINT unique_entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT unique_document_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON e.type",
            "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON e.name",
            "CREATE INDEX document_timestamp_index IF NOT EXISTS FOR (d:Document) ON d.timestamp"
        ]
        
        for query in constraints_queries:
            try:
                self.execute_query(query)
                self.logger.info(f"Constraint creado: {query}")
            except Exception as e:
                self.logger.warning(f"Error creando constraint: {str(e)}")
                
    def import_graph_data(self, graph_data: Dict[str, Any]) -> Dict[str, int]:
        """Importa datos de grafo en formato node-link alineado con ACAG-P"""
        stats = {"nodes_created": 0, "relationships_created": 0, "errors": 0}
        
        try:
            # Procesar nodos
            for node in graph_data.get("nodes", []):
                node_id = node.get("id")
                labels = node.get("labels", ["Entity"])
                properties = {k: v for k, v in node.items() 
                            if k not in ["id", "labels"] and v is not None}
                
                labels_str = ":".join(labels)
                query = f"MERGE (n:{labels_str} {{id: $id}}) SET n += $properties"
                self.execute_query(query, {"id": node_id, "properties": properties})
                stats["nodes_created"] += 1
                
            # Procesar relaciones
            for rel in graph_data.get("relationships", []):
                query = """
                MATCH (a {id: $source_id}), (b {id: $target_id})
                MERGE (a)-[r:%s]->(b)
                SET r += $properties
                """ % rel.get("type", "RELATED_TO")
                
                self.execute_query(query, {
                    "source_id": rel["source"],
                    "target_id": rel["target"],
                    "properties": {k: v for k, v in rel.items() 
                                 if k not in ["source", "target", "type"]}
                })
                stats["relationships_created"] += 1
                
        except Exception as e:
            stats["errors"] += 1
            self.logger.error(f"Error importando datos: {str(e)}")
            
        return stats
        
    def close(self) -> None:
        """Cierra la conexión con la base de datos"""
        if self.driver:
            self.driver.close()
            self.logger.info("Conexión Neo4j cerrada")
"""
Núcleo de Conocimiento Dual (NCD) - ACAG-P
Sistema de memoria dual que combina base de grafos y base vectorial
"""

from typing import Dict, Any
from .neo4j_manager import Neo4jManager
from .pinecone_manager import PineconeManager
from .data_router import DataRouter, DataType
from .query_client import UnifiedQueryClient
from .config_loader import NCDConfig
import logging

class DualKnowledgeCore:
    """Clase principal del Núcleo de Conocimiento Dual"""
    
    def __init__(self, config_path: str = "config/ncd_config.env"):
        self.config_loader = NCDConfig(config_path)
        self.config = self.config_loader.get_config()
        self.config_loader.setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.neo4j = None
        self.pinecone = None
        self.router = None
        self.query_client = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Inicializa todos los componentes del NCD"""
        try:
            self.logger.info("Inicializando Núcleo de Conocimiento Dual...")
            
            # Inicializar Neo4j
            neo4j_config = self.config["neo4j"]
            self.neo4j = Neo4jManager(
                uri=neo4j_config["uri"],
                user=neo4j_config["user"],
                password=neo4j_config["password"],
                database=neo4j_config["database"]
            )
            self.neo4j.create_constraints()
            
            # Inicializar Pinecone
            pinecone_config = self.config["pinecone"]
            self.pinecone = PineconeManager(
                api_key=pinecone_config["api_key"],
                environment=pinecone_config["environment"],
                index_name=pinecone_config["index_name"]
            )
            
            # Inicializar router y cliente de consultas
            self.router = DataRouter(self.neo4j, self.pinecone)
            self.query_client = UnifiedQueryClient(self.neo4j, self.pinecone)
            
            self.initialized = True
            self.logger.info("NCD inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando NCD: {str(e)}")
            self.initialized = False
            return False
            
    def process_data(self, data: Dict[str, Any], data_type: str = None) -> Dict[str, Any]:
        """Procesa datos a través del router del NCD"""
        if not self.initialized:
            raise RuntimeError("NCD no inicializado. Llame a initialize() primero.")
            
        # Determinar tipo de dato si no se especifica
        if data_type is None:
            detected_type = self.router.determine_data_type(data)
            data_type = detected_type.value
            
        # Convertir a enum
        try:
            data_type_enum = DataType(data_type)
        except ValueError:
            raise ValueError(f"Tipo de dato inválido: {data_type}")
            
        return self.router.route_data(data, data_type_enum)
        
    def query(self, query_type: str, **kwargs) -> Any:
        """Ejecuta consultas a través del cliente unificado"""
        if not self.initialized:
            raise RuntimeError("NCD no inicializado. Llame a initialize() primero.")
            
        query_methods = {
            "cypher": self.query_client.execute_cypher,
            "semantic": self.query_client.semantic_search,
            "hybrid": self.query_client.hybrid_search,
            "stats": self.query_client.get_system_stats
        }
        
        if query_type not in query_methods:
            raise ValueError(f"Tipo de consulta inválido: {query_type}")
            
        return query_methods[query_type](**kwargs)
        
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del NCD"""
        return {
            "initialized": self.initialized,
            "neo4j_connected": self.neo4j is not None,
            "pinecone_connected": self.pinecone is not None,
            "config": {
                "neo4j_database": self.config["neo4j"]["database"],
                "pinecone_index": self.config["pinecone"]["index_name"]
            }
        }
        
    def close(self) -> None:
        """Cierra todas las conexiones del NCD"""
        if self.neo4j:
            self.neo4j.close()
        self.logger.info("Conexiones NCD cerradas")
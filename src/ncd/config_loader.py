from typing import Dict, Any
import os
from dotenv import load_dotenv
import logging

class NCDConfig:
    """Cargador de configuración para el Núcleo de Conocimiento Dual"""
    
    def __init__(self, env_path: str = "config/ncd_config.env"):
        self.env_path = env_path
        self.config = {}
        self._load_environment()
        self._validate_config()
        
    def _load_environment(self) -> None:
        """Carga variables de entorno desde el archivo de configuración"""
        try:
            load_dotenv(self.env_path)
            
            self.config = {
                "neo4j": {
                    "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                    "user": os.getenv("NEO4J_USER", "neo4j"),
                    "password": os.getenv("NEO4J_PASSWORD", ""),
                    "database": os.getenv("NEO4J_DATABASE", "acag_knowledge"),
                    "max_connections": int(os.getenv("NEO4J_MAX_CONNECTIONS", "50"))
                },
                "pinecone": {
                    "api_key": os.getenv("PINECONE_API_KEY", ""),
                    "environment": os.getenv("PINECONE_ENVIRONMENT", ""),
                    "index_name": os.getenv("PINECONE_INDEX_NAME", "acag-knowledge"),
                    "timeout": int(os.getenv("PINECONE_TIMEOUT", "30"))
                },
                "embeddings": {
                    "model_name": os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
                    "dimension": int(os.getenv("EMBEDDING_DIMENSION", "384")),
                    "batch_size": int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
                },
                "performance": {
                    "query_timeout_ms": int(os.getenv("QUERY_TIMEOUT_MS", "5000"))
                }
            }
            
        except Exception as e:
            raise ValueError(f"Error cargando configuración: {str(e)}")
            
    def _validate_config(self) -> None:
        """Valida la configuración requerida"""
        required_fields = [
            ("neo4j", "uri"),
            ("neo4j", "user"),
            ("neo4j", "password"),
            ("pinecone", "api_key"),
            ("pinecone", "environment")
        ]
        
        missing_fields = []
        for section, field in required_fields:
            if not self.config[section][field]:
                missing_fields.append(f"{section}.{field}")
                
        if missing_fields:
            raise ValueError(f"Campos de configuración requeridos faltantes: {missing_fields}")
            
    def get_config(self) -> Dict[str, Any]:
        """Devuelve la configuración completa"""
        return self.config
        
    def setup_logging(self) -> None:
        """Configura el sistema de logging para NCD"""
        log_level = os.getenv("NCD_LOG_LEVEL", "INFO")
        log_file = os.getenv("NCD_LOG_FILE")
        
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename=log_file,
            filemode='a'
        )
        
        if log_file:
            logging.info(f"Logging configurado. Archivo: {log_file}")
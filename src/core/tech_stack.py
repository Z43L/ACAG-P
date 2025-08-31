from enum import Enum
from typing import Dict, Any

class TechStack:
    """Configuración centralizada del stack tecnológico ACAG-P"""
    
    class DatabaseType(Enum):
        NEO4J = "neo4j"
        PINECONE = "pinecone"
        REDIS = "redis"
        SQL = "postgresql"
    
    class MLFramework(Enum):
        TRANSFORMERS = "transformers"
        PYTORCH = "pytorch"
        PEFT = "peft"
        OPENROUTER = "openrouter"
    
    def __init__(self):
        self.components = {
            'databases': {
                self.DatabaseType.NEO4J: {
                    'version': '5.0+',
                    'driver': 'neo4j-python-driver',
                    'use_case': 'Conocimiento estructurado y relaciones'
                },
                self.DatabaseType.PINECONE: {
                    'version': '2.2+',
                    'driver': 'pinecone-client',
                    'use_case': 'Búsqueda semántica y embeddings'
                },
                self.DatabaseType.REDIS: {
                    'version': '7.0+',
                    'driver': 'redis-py',
                    'use_case': 'Caché y colas de mensajes'
                }
            },
            'ml_frameworks': {
                self.MLFramework.TRANSFORMERS: {
                    'version': '4.30+',
                    'use_case': 'Modelos de lenguaje y NLP'
                },
                self.MLFramework.PEFT: {
                    'version': '0.5+',
                    'use_case': 'Fine-tuning eficiente con LoRA'
                },
                self.MLFramework.OPENROUTER: {
                    'version': 'N/A',
                    'use_case': 'Acceso a modelos externos'
                }
            },
            'processing': {
                'spacy': {'version': '3.7+', 'use_case': 'NLP básico'},
                'celery': {'version': '5.3+', 'use_case': 'Tareas asíncronas'},
                'fastapi': {'version': '0.95+', 'use_case': 'API REST'}
            }
        }
    
    def get_requirements(self) -> Dict[str, str]:
        """Genera requirements.txt compatible con el stack"""
        return {
            'neo4j': '>=5.0,<6.0',
            'pinecone-client': '>=2.2.1',
            'redis': '>=4.5.0',
            'transformers': '>=4.30.0',
            'torch': '>=2.0.0',
            'peft': '>=0.5.0',
            'spacy': '>=3.7.0',
            'celery': '>=5.3.0',
            'fastapi': '>=0.95.0',
          'uvicorn': '>=0.22.0',
            'python-multipart': '>=0.0.6',
            'openai': '>=0.27.0',
            'requests': '>=2.31.0'
        }
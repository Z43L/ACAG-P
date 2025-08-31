from abc import ABC, abstractmethod
from typing import Any, Dict, List
from enum import Enum
from datetime import datetime

class ContentType(Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    DATABASE = "database"
    API = "api"

class BaseAdapter(ABC):
    """Clase base abstracta para todos los adaptadores del MIU"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.supported_types = []
        
    @abstractmethod
    def connect(self) -> bool:
        """Establece conexión con la fuente de datos"""
        pass
        
    @abstractmethod
    def extract_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """Extrae datos de la fuente y los devuelve en formato normalizado"""
        pass
        
    @abstractmethod
    def close(self) -> bool:
        """Cierra la conexión con la fuente"""
        pass
        
    def get_supported_types(self) -> List[ContentType]:
        """Devuelve los tipos de contenido soportados por este adaptador"""
        return self.supported_types

class TextAdapter(BaseAdapter):
    """Adaptador para procesamiento de texto plano y documentos"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_types = [ContentType.TEXT]
        self.encoding = config.get('encoding', 'utf-8')
        
    def connect(self) -> bool:
        # Para texto, la "conexión" es simplemente verificar accesibilidad
        return True
        
    def extract_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        source_path = parameters.get('path')
        try:
            with open(source_path, 'r', encoding=self.encoding) as file:
                content = file.read()
                
            return [{
                'content': content,
                'metadata': {
                    'source': source_path,
                    'type': ContentType.TEXT.value,
                    'size': len(content),
                    'timestamp': datetime.now().isoformat()
                }
            }]
        except Exception as e:
            raise Exception(f"Error reading text file {source_path}: {str(e)}")
            
    def close(self) -> bool:
        return True
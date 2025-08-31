import requests
from typing import Dict, List, Any
from .base_adapter import BaseAdapter, ContentType

class APIAdapter(BaseAdapter):
    """Adaptador para consumo de APIs RESTful"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_types = [ContentType.API]
        self.base_url = config.get('base_url', '')
        self.headers = config.get('headers', {})
        self.timeout = config.get('timeout', 30)
        
    def connect(self) -> bool:
        """Verifica la conectividad con la API"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                headers=self.headers,
                timeout=self.timeout
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
            
    def extract_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """Extrae datos de la API según los parámetros proporcionados"""
        endpoint = parameters.get('endpoint', '')
        params = parameters.get('params', {})
        
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return [{
                'content': response.json(),
                'metadata': {
                    'source': f"{self.base_url}/{endpoint}",
                    'type': ContentType.API.value,
                    'timestamp': datetime.now().isoformat(),
                    'response_size': len(response.content)
                }
            }]
        except requests.RequestException as e:
            raise Exception(f"Error accessing API: {str(e)}")
            
    def close(self) -> bool:
        """Cierra la conexión (no aplicable para APIs HTTP)"""
        return True
import sqlalchemy as sql
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime
from .base_adapter import BaseAdapter, ContentType

class DatabaseAdapter(BaseAdapter):
    """Adaptador para conexión con bases de datos SQL"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.supported_types = [ContentType.DATABASE]
        self.engine = None
        self.connection_string = config.get('connection_string')
        
    def connect(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            self.engine = sql.create_engine(self.connection_string)
            # Verificar conexión
            with self.engine.connect() as conn:
                conn.execute(sql.text("SELECT 1"))
            return True
        except Exception as e:
            raise Exception(f"Database connection failed: {str(e)}")
            
    def extract_data(self, parameters: Dict[str, Any]) -> List[Dict]:
        """Extrae datos mediante consulta SQL"""
        query = parameters.get('query')
        if not query:
            raise ValueError("SQL query is required for database adapter")
            
        try:
            with self.engine.connect() as conn:
                result = conn.execute(sql.text(query))
                df = pd.DataFrame(result.fetchall(), columns=result.keys())
                
                return [{
                    'content': df.to_dict('records'),
                    'metadata': {
                        'source': 'database',
                        'type': ContentType.DATABASE.value,
                        'query': query,
                        'row_count': len(df),
                        'timestamp': datetime.now().isoformat()
                    }
                }]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
            
    def close(self) -> bool:
        """Cierra la conexión con la base de datos"""
        if self.engine:
            self.engine.dispose()
        return True
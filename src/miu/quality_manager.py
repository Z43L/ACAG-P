from typing import Dict, List, Any
import re
from datetime import datetime

class DataQualityManager:
    """Gestiona la calidad y validación de los datos ingeridos"""
    
    def __init__(self):
        self.quality_metrics = {}
        self.validation_rules = {
            'min_text_length': 10,
            'max_text_length': 10000,
            'allowed_formats': ['json', 'xml', 'text', 'csv'],
            'required_metadata': ['source', 'type', 'timestamp']
        }
        
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida los datos según las reglas establecidas"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 0.0
        }
        
        # Validar contenido
        if 'content' not in data:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Missing content field')
            
        # Validar metadatos
        metadata = data.get('metadata', {})
        for field in self.validation_rules['required_metadata']:
            if field not in metadata:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'Missing metadata: {field}')
                
        # Validar longitud del texto
        if isinstance(data['content'], str):
            text_length = len(data['content'])
            if text_length < self.validation_rules['min_text_length']:
                validation_result['warnings'].append('Content too short')
            if text_length > self.validation_rules['max_text_length']:
                validation_result['is_valid'] = False
                validation_result['errors'].append('Content too long')
                
        # Calcular score de calidad
        validation_result['quality_score'] = self._calculate_quality_score(validation_result)
        
        return validation_result
        
    def _calculate_quality_score(self, validation_result: Dict[str, Any]) -> float:
        """Calcula un score de calidad basado en los resultados de validación"""
        base_score = 1.0
        
        # Penalizar por errores
        base_score -= len(validation_result['errors']) * 0.3
        
        # Penalizar levemente por warnings
        base_score -= len(validation_result['warnings']) * 0.1
        
        return max(0.0, min(1.0, base_score))
        
    def apply_data_cleaning(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica técnicas de limpieza y normalización de datos"""
        cleaned_data = data.copy()
        
        if isinstance(cleaned_data['content'], str):
            # Limpieza básica de texto
            cleaned_data['content'] = self._clean_text(cleaned_data['content'])
            
        # Normalización de metadatos
        cleaned_data['metadata'] = self._normalize_metadata(cleaned_data.get('metadata', {}))
        
        return cleaned_data
        
    def _clean_text(self, text: str) -> str:
        """Limpia y normaliza texto"""
        # Eliminar múltiples espacios
        text = re.sub(r'\s+', ' ', text)
        # Eliminar caracteres no imprimibles
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        # Normalizar saltos de línea
        text = re.sub(r'\r\n', '\n', text)
        
        return text.strip()
        
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza los metadatos a un formato estándar"""
        normalized = metadata.copy()
        
        # Asegurar timestamp en formato ISO
        if 'timestamp' in normalized and not isinstance(normalized['timestamp'], str):
            normalized['timestamp'] = datetime.now().isoformat()
        elif 'timestamp' not in normalized:
            normalized['timestamp'] = datetime.now().isoformat()
            
        # Normalizar tipo de contenido
        if 'type' in normalized:
            normalized['type'] = str(normalized['type']).lower()
            
        return normalized
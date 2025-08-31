from typing import Dict, List, Any
import re
from datetime import datetime
import hashlib

class DataQualityValidator:
    """Valida y asegura la calidad de los datos ingeridos"""
    
    def __init__(self):
        self.validation_rules = {
            'min_text_length': 10,
            'max_text_length': 100000,
            'allowed_content_types': ['text', 'json', 'xml'],
            'required_metadata_fields': ['source', 'type', 'timestamp']
        }
        
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta validaciones completas sobre los datos"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'quality_score': 1.0
        }
        
        # Validar estructura básica
        if 'content' not in data:
            validation_result['is_valid'] = False
            validation_result['errors'].append('Missing content field')
            
        # Validar metadatos
        metadata = data.get('metadata', {})
        for field in self.validation_rules['required_metadata_fields']:
            if field not in metadata:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f'Missing metadata field: {field}')
                
        # Validar contenido
        if isinstance(data.get('content'), str):
            content = data['content']
            if len(content) < self.validation_rules['min_text_length']:
                validation_result['warnings'].append('Content is too short')
                validation_result['quality_score'] *= 0.8
                
            if len(content) > self.validation_rules['max_text_length']:
                validation_result['warnings'].append('Content is too long')
                validation_result['quality_score'] *= 0.9
                
            # Validar caracteres no válidos
            invalid_chars = self._find_invalid_characters(content)
            if invalid_chars:
                validation_result['warnings'].append(f'Invalid characters found: {invalid_chars}')
                validation_result['quality_score'] *= 0.95
                
        return validation_result
        
    def _find_invalid_characters(self, text: str) -> List[str]:
        """Encuentra caracteres no válidos en el texto"""
        # Caracteres de control ASCII (excepto tab, newline, carriage return)
        invalid_pattern = re.compile(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]')
        invalid_matches = invalid_pattern.findall(text)
        return list(set(invalid_matches))  # Devolver únicos
        
    def generate_fingerprint(self, data: Dict[str, Any]) -> str:
        """Genera huella digital única para detección de duplicados"""
        content = str(data.get('content', ''))
        metadata = str(data.get('metadata', {}))
        
        # Crear hash del contenido and metadatos relevantes
        fingerprint_data = content + metadata
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
        
    def normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza los datos a formato estándar"""
        normalized = data.copy()
        
        # Normalizar metadatos
        if 'metadata' in normalized:
            normalized['metadata'] = self._normalize_metadata(normalized['metadata'])
            
        # Normalizar contenido
        if isinstance(normalized.get('content'), str):
            normalized['content'] = self._normalize_content(normalized['content'])
            
        return normalized
        
    def _normalize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza los metadatos a formato estándar"""
        normalized = metadata.copy()
        
        # Asegurar timestamp en formato ISO
        if 'timestamp' in normalized:
            if not isinstance(normalized['timestamp'], str):
                normalized['timestamp'] = datetime.now().isoformat()
        else:
            normalized['timestamp'] = datetime.now().isoformat()
            
        # Normalizar tipo de contenido
        if 'type' in normalized:
            normalized['type'] = str(normalized['type']).lower()
            
        return normalized
        
    def _normalize_content(self, content: str) -> str:
        """Normaliza el contenido de texto"""
        # Eliminar múltiples espacios y saltos de línea
        content = re.sub(r'\s+', ' ', content)
        # Eliminar caracteres de control
        content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', content)
        # Normalizar encoding
        content = content.encode('utf-8', 'ignore').decode('utf-8')
        
        return content.strip()
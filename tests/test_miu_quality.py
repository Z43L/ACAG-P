import pytest
from src.miu.quality_validator import DataQualityValidator

class TestDataQualityValidator:
    """Pruebas para el validador de calidad de datos"""
    
    def setUp(self):
        self.validator = DataQualityValidator()
    
    def test_validation_valid_data(self):
        """Prueba validación de datos válidos"""
        data = {
            'content': 'Texto de prueba con suficiente longitud para pasar validación',
            'metadata': {
                'source': 'test_source',
                'type': 'text',
                'timestamp': '2023-01-01T00:00:00'
            }
        }
        
        result = self.validator.validate(data)
        assert result['is_valid'] == True
        assert result['quality_score'] > 0.8
    
    def test_validation_missing_content(self):
        """Prueba validación de datos sin contenido"""
        data = {
            'metadata': {'source': 'test'}
        }
        
        result = self.validator.validate(data)
        assert result['is_valid'] == False
        assert 'Missing content field' in result['errors']
    
    def test_validation_short_content(self):
        """Prueba validación de contenido muy corto"""
        data = {
            'content': 'Hola',
            'metadata': {'source': 'test', 'type': 'text', 'timestamp': '2023-01-01T00:00:00'}
        }
        
        result = self.validator.validate(data)
        assert result['is_valid'] == True  # Aún válido pero con advertencia
        assert result['quality_score'] < 0.9
        assert 'Content is too short' in result['warnings']
    
    def test_fingerprint_generation(self):
        """Prueba generación de huella digital para detección de duplicados"""
        data = {
            'content': 'Texto idéntico',
            'metadata': {'source': 'test'}
        }
        
        fingerprint1 = self.validator.generate_fingerprint(data)
        fingerprint2 = self.validator.generate_fingerprint(data)
        
        # Deben ser idénticos para el mismo contenido
        assert fingerprint1 == fingerprint2
        
        # Deben ser diferentes para contenido diferente
        data2 = {'content': 'Texto diferente', 'metadata': {'source': 'test'}}
        fingerprint3 = self.validator.generate_fingerprint(data2)
        assert fingerprint1 != fingerprint3
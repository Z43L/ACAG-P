import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from src.miu.adapters.text_adapter import TextAdapter
from src.miu.adapters.api_adapter import APIAdapter
from src.miu.adapters.database_adapter import DatabaseAdapter

class TestTextAdapter:
    """Pruebas para el adaptador de texto"""
    
    def test_text_adapter_initialization(self):
        """Prueba que el adaptador de texto se inicialice correctamente"""
        config = {'encoding': 'utf-8'}
        adapter = TextAdapter(config)
        assert adapter.encoding == 'utf-8'
        assert adapter.supported_types == ['text']
    
    def test_text_extraction_valid_file(self):
        """Prueba extracción de texto desde archivo válido"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Este es un texto de prueba para el adaptador")
            f.flush()
            
            adapter = TextAdapter({})
            result = adapter.extract_data({'path': f.name})
            
            assert len(result) == 1
            assert result[0]['content'] == "Este es un texto de prueba para el adaptador"
            assert result[0]['metadata']['type'] == 'text'
            
        os.unlink(f.name)
    
    def test_text_extraction_invalid_file(self):
        """Prueba manejo de archivo inexistente"""
        adapter = TextAdapter({})
        with pytest.raises(Exception, match="Error reading text file"):
            adapter.extract_data({'path': '/ruta/inexistente.txt'})

class TestAPIAdapter:
    """Pruebas para el adaptador de API"""
    
    @patch('requests.get')
    def test_api_adapter_successful_request(self, mock_get):
        """Prueba solicitud API exitosa"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_get.return_value = mock_response
        
        config = {'base_url': 'https://api.example.com', 'timeout': 30}
        adapter = APIAdapter(config)
        result = adapter.extract_data({'endpoint': 'test', 'params': {}})
        
        assert len(result) == 1
        assert result[0]['content'] == {'data': 'test'}
        mock_get.assert_called_with(
            'https://api.example.com/test',
            headers={},
            params={},
            timeout=30
        )
    
    @patch('requests.get')
    def test_api_adapter_failed_request(self, mock_get):
        """Prueba manejo de error en API"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        adapter = APIAdapter({})
        with pytest.raises(Exception, match="Error accessing API"):
            adapter.extract_data({'endpoint': 'test'})

class TestDatabaseAdapter:
    """Pruebas para el adaptador de base de datos"""
    
    @patch('sqlalchemy.create_engine')
    def test_database_connection(self, mock_engine):
        """Prueba conexión a base de datos"""
        mock_conn = Mock()
        mock_engine.return_value.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.return_value.connect.return_value.__exit__ = Mock(return_value=None)
        
        config = {'connection_string': 'postgresql://user:pass@localhost/db'}
        adapter = DatabaseAdapter(config)
        
        assert adapter.connect() == True
    
    def test_database_query_validation(self):
        """Prueba validación de query requerida"""
        adapter = DatabaseAdapter({})
        with pytest.raises(ValueError, match="SQL query is required"):
            adapter.extract_data({})
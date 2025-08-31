import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.ncd.pinecone_manager import PineconeManager

class TestPineconeIntegration:
    """Pruebas de integración con Pinecone"""
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.create_index')
    @patch('pinecone.Index')
    def test_pinecone_initialization(self, mock_index, mock_create, mock_list, mock_init):
        """Prueba inicialización de Pinecone"""
        mock_list.return_value = []  # No existen índices
        
        manager = PineconeManager("test-api-key", "test-environment", "test-index")
        
        mock_init.assert_called_with(api_key="test-api-key", environment="test-environment")
        mock_create.assert_called_once()
        assert manager.index is not None
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_upsert_vectors(self, mock_index, mock_list, mock_init):
        """Prueba upsert de vectores en Pinecone"""
        mock_list.return_value = ["test-index"]
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        mock_index_instance.upsert.return_value = {"upserted_count": 1}
        
        manager = PineconeManager("test-api-key", "test-environment", "test-index")
        
        vectors = [{
            "id": "vec1",
            "embeddings": np.array([0.1, 0.2, 0.3]),
            "metadata": {"text": "test"}
        }]
        
        result = manager.upsert_vectors(vectors)
        assert result["upserted_count"] == 1
        mock_index_instance.upsert.assert_called_once()
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_semantic_search(self, mock_index, mock_list, mock_init):
        """Prueba búsqueda semántica en Pinecone"""
        mock_list.return_value = ["test-index"]
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        mock_index_instance.query.return_value = {
            "matches": [
                {"id": "result1", 'score': 0.9, "metadata": {"text": "relevant"}}
            ]
        }
        
        manager = PineconeManager("test-api-key", "test-environment", "test-index")
        
        results = manager.semantic_search("test query", top_k=5)
        assert len(results) == 1
        assert results[0]["id"] == "result1"
        assert results[0]["score"] == 0.9
    
    @patch('pinecone.init')
    @patch('pinecone.list_indexes')
    @patch('pinecone.Index')
    def test_hybrid_search(self, mock_index, mock_list, mock_init):
        """Prueba búsqueda híbrida"""
        mock_list.return_value = ["test-index"]
        mock_index_instance = Mock()
        mock_index.return_value = mock_index_instance
        mock_index_instance.query.return_value = {
            "matches": [
                {"id": "result1", "score": 0.9, "metadata": {"text": "test relevant"}},
                {"id": "result2", "score": 0.8, "metadata": {"text": "other"}}
            ]
        }
        
        manager = PineconeManager("test-api-key", "test-environment", "test-index")
        
        results = manager.hybrid_search(
            np.array([0.1, 0.2, 0.3]),
            keyword="test",
            top_k=2
        )
        
        # Debería filtrar resultados basado en keyword
        assert len(results) <= 2
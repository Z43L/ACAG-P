import pytest
from unittest.mock import Mock, patch
from src.art.model_router import ModelRouter, QueryComplexity, ModelType

class TestModelRouter:
    """Pruebas para el router de modelos del ART"""
    
    @patch('transformers.pipeline')
    @patch('openai.OpenAI')
    def test_router_initialization(self, mock_openai, mock_pipeline):
        """Prueba inicialización del router"""
        mock_pipeline.return_value = Mock()
        mock_openai.return_value = Mock()
        
        router = ModelRouter("local-model-path", "openrouter-api-key")
        assert router.local_model is not None
        assert router.openrouter is not None
    
    def test_query_complexity_analysis(self):
        """Prueba análisis de complejidad de consultas"""
        router = ModelRouter("test", "test")
        
        # Consulta simple
        complexity = router.analyze_query("What is the capital of France?", {})
        assert complexity == QueryComplexity.SIMPLE
        
        # Consulta compleja
        complexity = router.analyze_query("Explain how neural networks work", {})
        assert complexity == QueryComplexity.COMPLEX
        
        # Consulta creativa
        complexity = router.analyze_query("Write a poem about technology", {})
        assert complexity == QueryComplexity.CREATIVE
    
    def test_model_selection(self):
        """Prueba selección de modelo basado en complejidad"""
        router = ModelRouter("test", "test")
        
        # Consulta simple -> Modelo local
        model_type = router.select_model(QueryComplexity.SIMPLE, {})
        assert model_type == ModelType.LOCAL
        
        # Consulta compleja -> Modelo híbrido
        model_type = router.select_model(QueryComplexity.COMPLEX, {})
        assert model_type == ModelType.HYBRID
        
        # Consulta creativa -> Modelo externo
        model_type = router.select_model(QueryComplexity.CREATIVE, {})
        assert model_type == ModelType.EXTERNAL
    
    @patch('transformers.pipeline')
    def test_local_model_query(self, mock_pipeline):
        """Prueba consulta al modelo local"""
        mock_model = Mock()
        mock_model.return_value = [{'generated_text': 'Respuesta de prueba'}]
        mock_pipeline.return_value = mock_model
        
        router = ModelRouter("test", "test")
        response = router.query_local_model("Test query", "Test context")
        
        assert response == "Respuesta de prueba"
        mock_model.assert_called_once()
    
    @patch('openai.OpenAI')
    def test_external_model_query(self, mock_openai):
        """Prueba consulta a modelo externo via OpenRouter"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Respuesta externa"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        router = ModelRouter("test", "test")
        response = router.query_external_model("Test query", "Test context")
        
        assert response == "Respuesta externa"
        mock_client.chat.completions.create.assert_called_once()
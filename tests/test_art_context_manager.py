import pytest
from unittest.mock import Mock, patch
from src.art.context_manager import ContextManager

class TestContextManager:
    """Pruebas para el gestor de contexto del ART"""
    
    @patch('src.ncd.neo4j_manager.Neo4jManager')
    def test_context_initialization(self, mock_ncd):
        """Prueba inicialización del gestor de contexto"""
        mock_ncd_instance = Mock()
        mock_ncd.return_value = mock_ncd_instance
        
        manager = ContextManager(mock_ncd_instance, max_history=5)
        assert manager.ncd_client is not None
        assert manager.max_history == 5
    
    def test_conversation_history_management(self):
        """Prueba gestión del historial de conversación"""
        ncd_client = Mock()
        manager = ContextManager(ncd_client)
        
        user_id = "test_user"
        
        # Añadir varias interacciones
        for i in range(10):
            manager.update_conversation_history(user_id, f"query_{i}", f"response_{i}")
        
        # Obtener contexto
        context = manager.get_context(user_id, "nueva_consulta")
        
        # Debería mantener solo las últimas 5 interacciones (max_history por defecto)
        assert len(context.conversation_history) == 5
        assert context.conversation_history[0]['query'] == "query_5"  # Primera de las últimas 5
    
    @patch('src.ncd.neo4j_manager.Neo4jManager')
    def test_knowledge_context_retrieval(self, mock_ncd):
        """Prueba recuperación de contexto de conocimiento"""
        mock_ncd_instance = Mock()
        mock_ncd_instance.semantic_search.return_value = [
            {'id': '1', 'score': 0.9, 'metadata': {'text': 'conocimiento relevante'}}
        ]
        mock_ncd_instance.find_entities.return_value = [{'id': 'ent1', 'name': 'Test Entity'}]
        
        manager = ContextManager(mock_ncd_instance)
        context = manager._get_knowledge_context("consulta de prueba")
        
        assert 'semantic_results' in context
        assert 'graph_context' in context
        assert len(context['semantic_results']) == 1
        mock_ncd_instance.semantic_search.assert_called_once()
    
    def test_temporal_context_generation(self):
        """Prueba generación de contexto temporal"""
        ncd_client = Mock()
        manager = ContextManager(ncd_client)
        
        context = manager._get_temporal_context()
        
        assert 'timestamp' in context
        assert 'time_of_day' in context
        assert 'day_of_week' in context
        assert 'season' in context
        assert context['season'] in ['winter', 'spring', 'summer', 'autumn']
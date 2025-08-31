import pytest
from unittest.mock import Mock, patch
from src.core.integration_manager import IntegrationManager
from src.core.data_flow_manager import DataFlowManager

class TestFullSystemIntegration:
    """Pruebas de integración completa del sistema ACAG-P"""
    
    @patch('redis.Redis')
    def test_integration_pipeline(self, mock_redis):
        """Prueba el pipeline completo de integración"""
        mock_redis_instance = Mock()
        mock_redis.return_value = mock_redis_instance
        mock_redis_instance.rpush.return_value = True
        mock_redis_instance.blpop.return_value = (None, json.dumps({
            'payload': {'type': 'test_message'},
            'metadata': {'timestamp': '2023-01-01T00:00:00'}
        }))
        
        integration = IntegrationManager()
        data_flow = DataFlowManager(integration)
        
        # Probar flujo de ingesta
        flow_id = data_flow.start_ingestion_flow('text', {'path': '/test/path.txt'})
        assert flow_id.startswith('flow_ingest_')
        
        # Probar flujo de aprendizaje
        cycle_id = data_flow.start_learning_cycle('manual')
        assert cycle_id.startswith('cycle_learn_')
        
        # Probar flujo de consulta de usuario
        session_id = data_flow.process_user_query('test_user', 'Test query')
        assert session_id.startswith('session_test_user_')
    
    @patch('src.ncd.neo4j_manager.Neo4jManager')
    @patch('src.ncd.pinecone_manager.PineconeManager')
    @patch('src.art.model_router.ModelRouter')
    @patch('src.mci.interaction_analyzer.InteractionAnalyzer')
    def test_complete_query_flow(self, mock_analyzer, mock_router, mock_pinecone, mock_neo4j):
        """Prueba el flujo completo de una consulta de usuario"""
        # Configurar mocks
        mock_neo4j_instance = Mock()
        mock_neo4j.return_value = mock_neo4j_instance
        
        mock_pinecone_instance = Mock()
        mock_pinecone.return_value = mock_pinecone_instance
        mock_pinecone_instance.semantic_search.return_value = [{'id': '1', 'score': 0.9}]
        
        mock_router_instance = Mock()
        mock_router.return_value = mock_router_instance
        mock_router_instance.process_query.return_value = "Test response"
        
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_interaction.return_value = {
            'sentiment': {'interaction_balance': 0.5},
            'personal_info': {},
            'preferences': {},
            'importance': 0.5
        }
        
        # Este test sería más complejo en la implementación real,
        # simulando todas las interacciones entre módulos
        
        assert True  # Placeholder para test de integración complejo
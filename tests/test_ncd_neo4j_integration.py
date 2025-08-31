import pytest
from unittest.mock import Mock, patch
from src.ncd.neo4j_manager import Neo4jManager

class TestNeo4jIntegration:
    """Pruebas de integración con Neo4j"""
    
    @patch('neo4j.GraphDatabase.driver')
    def test_connection_verification(self, mock_driver):
        """Prueba verificación de conexión con Neo4j"""
        mock_session = Mock()
        mock_session.run.return_value.single.return_value = {"test": 1}
        mock_driver.return_value.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.return_value.session.return_value.__exit__ = Mock(return_value=None)
        
        manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
        assert manager._verify_connection() == True
    
    @patch('neo4j.GraphDatabase.driver')
    def test_query_execution(self, mock_driver):
        """Prueba ejecución de queries Cypher"""
        mock_session = Mock()
        mock_session.run.return_value = [{"result": "data"}]
        mock_driver.return_value.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.return_value.session.return_value.__exit__ = Mock(return_value=None)
        
        manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
        results = manager.execute_query("MATCH (n) RETURN n")
        
        assert len(results) == 1
        assert results[0]["result"] == "data"
    
    @patch('neo4j.GraphDatabase.driver')
    def test_constraint_creation(self, mock_driver):
        """Prueba creación de constraints"""
        mock_session = Mock()
        mock_session.run.return_value = Mock()
        mock_driver.return_value.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.return_value.session.return_value.__exit__ = Mock(return_value=None)
        
        manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
        manager.create_constraints()
        
        # Verificar que se ejecutaron queries de constraints
        assert mock_session.run.call_count >= 4  # Múltiples constraints
    
    @patch('neo4j.GraphDatabase.driver')
    def test_graph_data_import(self, mock_driver):
        """Prueba importación de datos de grafo"""
        mock_session = Mock()
        mock_session.run.return_value = Mock()
        mock_driver.return_value.session.return_value.__enter__ = Mock(return_value=mock_session)
        mock_driver.return_value.session.return_value.__exit__ = Mock(return_value=None)
        
        manager = Neo4jManager("bolt://localhost:7687", "neo4j", "password")
        
        graph_data = {
            "nodes": [
                {"id": "1", "labels": ["Entity"], "name": "Test Node"}
            ],
            "relationships": [
                {"source": "1", "target": "2", "type": "RELATED_TO"}
            ]
        }
        
        stats = manager.import_graph_data(graph_data)
        assert stats["nodes_created"] == 1
        assert stats["relationships_created"] == 1
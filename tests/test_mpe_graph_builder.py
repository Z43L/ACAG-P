import pytest
import networkx as nx
from src.mpe.graph_builder import KnowledgeGraphBuilder

class TestKnowledgeGraphBuilder:
    """Pruebas para el constructor de grafos de conocimiento"""
    
    def setUp(self):
        self.builder = KnowledgeGraphBuilder()
    
    def test_graph_initialization(self):
        """Prueba que el grafo se inicialice correctamente"""
        assert isinstance(self.builder.graph, nx.MultiDiGraph)
        assert len(self.builder.graph.nodes) == 0
        assert len(self.builder.graph.edges) == 0
    
    def test_add_document_with_entities(self):
        """Prueba añadir documento con entidades"""
        processed_data = {
            'raw_text': 'Apple es una empresa de tecnología.',
            'entities': [
                {'text': 'Apple', 'label': 'ORG', 'start_char': 0, 'end_char': 5}
            ],
            'relations': [
                {'source': 'Apple', 'target': 'empresa', 'relation': 'es', 'confidence': 0.9}
            ],
            'metadata': {}
        }
        
        self.builder.add_document(processed_data)
        
        # Verificar que se añadieron nodos y relaciones
        assert len(self.builder.graph.nodes) == 2  # Documento + entidad
        assert len(self.builder.graph.edges) == 1
        
        # Verificar propiedades de los nodos
        assert 'Apple' in self.builder.graph.nodes
        assert self.builder.graph.nodes['Apple']['type'] == 'Entity'
    
    def test_export_graph_formats(self):
        """Prueba exportación en diferentes formatos"""
        # Añadir algunos datos de prueba
        processed_data = {
            'raw_text': 'Test document',
            'entities': [{'text': 'Test', 'label': 'MISC', 'start_char': 0, 'end_char': 4}],
            'relations': [],
            'metadata': {}
        }
        self.builder.add_document(processed_data)
        
        # Probar exportación a NetworkX
        nx_graph = self.builder.export_graph('networkx')
        assert isinstance(nx_graph, nx.MultiDiGraph)
        
        # Probar exportación a dict
        graph_dict = self.builder.export_graph('dict')
        assert 'nodes' in graph_dict
        assert 'links' in graph_dict
        
        # Probar exportación a Cypher
        cypher_queries = self.builder.export_graph('cypher')
        assert isinstance(cypher_queries, list)
        assert len(cypher_queries) > 0
        assert any('CREATE' in query for query in cypher_queries)
    
    def test_empty_document_handling(self):
        """Prueba manejo de documento sin entidades"""
        processed_data = {
            'raw_text': 'Texto sin entidades relevantes.',
            'entities': [],
            'relations': [],
            'metadata': {}
        }
        
        self.builder.add_document(processed_data)
        
        # Solo debería añadir el nodo del documento
        assert len(self.builder.graph.nodes) == 1
        assert len(self.builder.graph.edges) == 0
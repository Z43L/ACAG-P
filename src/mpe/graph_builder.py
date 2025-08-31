import networkx as nx
from typing import Dict, List, Any
from datetime import datetime

class KnowledgeGraphBuilder:
    """Construye y gestiona grafos de conocimiento a partir de datos procesados"""
    
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.entity_counter = 0
        
    def add_document(self, processed_data: Dict[str, Any]) -> None:
        """Añade un documento procesado al grafo de conocimiento"""
        doc_id = f"doc_{datetime.now().timestamp()}_{self.entity_counter}"
        self.entity_counter += 1
        
        # Añadir documento como nodo
        self.graph.add_node(doc_id, **{
            'type': 'Document',
            'text': processed_data['raw_text'],
            'metadata': processed_data.get('metadata', {})
        })
        
        # Procesar entidades y relaciones
        for entity in processed_data.get('entities', []):
            self._process_entity(entity, doc_id)
            
        # Procesar relaciones sintácticas
        for sentence in processed_data.get('syntax', {}).get('sentences', []):
            self._process_syntax(sentence, doc_id)
            
    def _process_entity(self, entity: Dict[str, Any], doc_id: str) -> None:
        """Procesa una entidad y sus relaciones"""
        entity_id = f"entity_{entity['word']}_{hash(entity['word'])}"
        
        # Añadir entidad como nodo
        self.graph.add_node(entity_id, **{
            'type': 'Entity',
            'text': entity['word'],
            'entity_type': entity['entity_group'],
            'confidence': entity['score']
        })
        
        # Conectar entidad con documento
        self.graph.add_edge(doc_id, entity_id, relationship='contains')
        
    def _process_syntax(self, sentence: Dict[str, Any], doc_id: str) -> None:
        """Procesa relaciones sintácticas"""
        for dependency in sentence.get('dependencies', []):
            source, rel_type, target = dependency
            
            source_id = f"token_{hash(source)}"
            target_id = f"token_{hash(target)}"
            
            # Añadir tokens como nodos
            self.graph.add_node(source_id, type='Token', text=source)
            self.graph.add_node(target_id, type='Token', text=target)
            
            # Añadir relación de dependencia
            self.graph.add_edge(
                source_id, 
                target_id, 
                relationship=rel_type,
                sentence=sentence['text']
            )
            
            # Conectar tokens con documento
            self.graph.add_edge(doc_id, source_id, relationship='contains')
            self.graph.add_edge(doc_id, target_id, relationship='contains')
            
    def export_graph(self, format: str = 'networkx') -> Any:
        """Exporta el grafo en el formato especificado"""
        if format == 'networkx':
            return self.graph
        elif format == 'dict':
            return nx.node_link_data(self.graph)
        elif format == 'cypher':
            return self._generate_cypher_queries()
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _generate_cypher_queries(self) -> List[str]:
        """Genera queries Cypher para importar el grafo en Neo4j"""
        queries = []
        
        # Crear nodos
        for node, attributes in self.graph.nodes(data=True):
            props = ', '.join([f"{k}: '{v}'" for k, v in attributes.items() if v is not None])
            queries.append(f"CREATE (n:{attributes.get('type', 'Node')} {{id: '{node}', {props}}})")
            
        # Crear relaciones
        for source, target, attributes in self.graph.edges(data=True):
            rel_type = attributes.get('relationship', 'RELATED_TO')
            props = ', '.join([f"{k}: '{v}'" for k, v in attributes.items() if k != 'relationship'])
            props_str = f" {{{props}}}" if props else ""
            queries.append(
                f"MATCH (a), (b) WHERE a.id = '{source}' AND b.id = '{target}' "
                f"CREATE (a)-[r:{rel_type}{props_str}]->(b)"
            )
            
        return queries
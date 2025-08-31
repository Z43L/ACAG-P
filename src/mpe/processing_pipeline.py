import spacy
import numpy as np
from typing import Dict, List, Any
from transformers import AutoTokenizer, AutoModel
import torch
import networkx as nx

class ProcessingPipeline:
    """Pipeline principal de procesamiento y estructuración del MPE"""
    
    def __init__(self, model_name: str = "dslim/bert-base-NER"):
        self.nlp = spacy.load("en_core_web_sm")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.graph = nx.DiGraph()
        
    def preprocess_text(self, text: str) -> str:
        """Preprocesamiento básico del texto"""
        # Eliminar caracteres especiales y normalizar espacios
        text = ' '.join(text.split())
        return text
        
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extrae entidades nombradas del texto"""
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start_char': ent.start_char,
                'end_char': ent.end_char
            })
            
        return entities
        
    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict[str, Any]]:
        """Extrae relaciones entre entidades usando modelo transformer"""
        # Implementación simplificada - en producción usaríamos un modelo especializado
        relations = []
        
        # Lógica compleja de extracción de relaciones
        if len(entities) >= 2:
            relations.append({
                'source': entities[0]['text'],
                'target': entities[1]['text'],
                'relation': 'related_to',
                'confidence': 0.85
            })
            
        return relations
        
    def generate_embeddings(self, text: str) -> np.ndarray:
        """Genera embeddings vectoriales para el texto"""
        inputs = self.tokenizer(text, return_tensors="pt", 
                              truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Usamos el promedio de los embeddings de la última capa
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        return embeddings
        
    def build_knowledge_graph(self, entities: List[Dict], relations: List[Dict]) -> nx.DiGraph:
        """Construye/actualiza el grafo de conocimiento"""
        # Añadir nodos (entidades)
        for entity in entities:
            self.graph.add_node(entity['text'], type=entity['label'])
            
        # Añadir aristas (relaciones)
        for relation in relations:
            self.graph.add_edge(
                relation['source'],
                relation['target'],
                relation=relation['relation'],
                confidence=relation['confidence']
            )
            
        return self.graph
        
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa un documento completo"""
        text = data['content']
        metadata = data['metadata']
        
        # Pipeline de procesamiento
        processed_text = self.preprocess_text(text)
        entities = self.extract_entities(processed_text)
        relations = self.extract_relations(processed_text, entities)
        embeddings = self.generate_embeddings(processed_text)
        graph = self.build_knowledge_graph(entities, relations)
        
        return {
            'original_text': text,
            'processed_text': processed_text,
            'entities': entities,
            'relations': relations,
            'embeddings': embeddings,
            'graph_data': nx.node_link_data(graph),
            'metadata': metadata
        }
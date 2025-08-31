import spacy
import numpy as np
from typing import Dict, List, Any
from transformers import AutoTokenizer, AutoModel, pipeline
import torch

class NLPPipeline:
    """Pipeline completo de procesamiento de lenguaje natural"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.nlp = spacy.load("en_core_web_sm")
        self.ner_model = pipeline(
            "ner",
            model=model_config.get('ner_model', "dslim/bert-base-NER"),
            aggregation_strategy="simple"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_config.get('embedding_model', "sentence-transformers/all-MiniLM-L6-v2")
        )
        self.embedding_model = AutoModel.from_pretrained(
            model_config.get('embedding_model', "sentence-transformers/all-MiniLM-L6-v2")
        )
        
    def process_text(self, text: str) -> Dict[str, Any]:
        """Procesa un texto completo through the NLP pipeline"""
        # Procesamiento con spaCy para análisis básico
        doc = self.nlp(text)
        
        # Extracción de entidades con transformer
        entities = self.ner_model(text)
        
        # Generación de embeddings
        embeddings = self._generate_embeddings(text)
        
        # Análisis de dependencias y sintaxis
        syntax_analysis = self._analyze_syntax(doc)
        
        return {
            'raw_text': text,
            'processed_text': doc.text,
            'entities': entities,
            'embeddings': embeddings,
            'syntax': syntax_analysis,
            'metadata': {
                'char_count': len(text),
                'word_count': len(doc),
                'sentence_count': len(list(doc.sents))
            }
        }
        
    def _generate_embeddings(self, text: str) -> np.ndarray:
        """Genera embeddings vectoriales para el texto"""
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.embedding_model(**inputs)
            
        # Usar el promedio de los embeddings de la última capa
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        return embeddings
        
    def _analyze_syntax(self, doc) -> Dict[str, Any]:
        """Analiza la sintaxis y estructura del texto"""
        return {
            'sentences': [{
                'text': sent.text,
                'root': sent.root.text,
                'dependencies': [
                    (token.text, token.dep_, token.head.text) 
                    for token in sent
                ]
            } for sent in doc.sents],
            'noun_phrases': [chunk.text for chunk in doc.noun_chunks],
            'verbs': [token.lemma_ for token in doc if token.pos_ == 'VERB']
        }
import pytest
import numpy as np
from unittest.mock import Mock, patch
from src.mpe.nlp_pipeline import NLPPipeline

class TestNLPPipeline:
    """Pruebas para el pipeline de procesamiento de lenguaje natural"""
    
    @patch('spacy.load')
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModel.from_pretrained')
    def test_pipeline_initialization(self, mock_model, mock_tokenizer, mock_spacy):
        """Prueba inicialización del pipeline NLP"""
        mock_nlp = Mock()
        mock_spacy.return_value = mock_nlp
        
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        
        pipeline = NLPPipeline({'ner_model': 'test-model', 'embedding_model': 'test-embedding'})
        assert pipeline.nlp is not None
        mock_spacy.assert_called_with("en_core_web_sm")
    
    def test_text_preprocessing(self):
        """Prueba preprocesamiento básico de texto"""
        pipeline = NLPPipeline({})
        text = "  Texto   con    espacios    excesivos  \n y saltos de línea.  "
        processed = pipeline.preprocess_text(text)
        
        assert processed == "Texto con espacios excesivos y saltos de línea."
        assert "  " not in processed  # No debería tener espacios múltiples
    
    @patch('transformers.AutoTokenizer')
    @patch('transformers.AutoModel')
    def test_embedding_generation(self, mock_model, mock_tokenizer):
        """Prueba generación de embeddings"""
        # Configurar mocks
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {'input_ids': Mock(), 'attention_mask': Mock()}
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        mock_model_instance = Mock()
        mock_model_instance.return_value.last_hidden_state = Mock()
        mock_model_instance.return_value.last_hidden_state.mean.return_value = Mock()
        mock_model_instance.return_value.last_hidden_state.mean.return_value.squeeze.return_value = Mock()
        mock_model_instance.return_value.last_hidden_state.mean.return_value.squeeze.return_value.numpy.return_value = np.array([0.1] * 384)
        mock_model.from_pretrained.return_value = mock_model_instance
        
        pipeline = NLPPipeline({})
        embeddings = pipeline.generate_embeddings("Texto de prueba")
        
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 384  # Dimensión del modelo de prueba
    
    def test_entity_extraction(self):
        """Prueba extracción de entidades con spaCy mock"""
        pipeline = NLPPipeline({})
        
        # Mock de documento de spaCy con entidades
        mock_doc = Mock()
        mock_ent = Mock()
        mock_ent.text = "Google"
        mock_ent.label_ = "ORG"
        mock_ent.start_char = 0
        mock_ent.end_char = 6
        
        mock_doc.ents = [mock_ent]
        pipeline.nlp = Mock(return_value=mock_doc)
        
        entities = pipeline.extract_entities("Google es una empresa")
        
        assert len(entities) == 1
        assert entities[0]['text'] == "Google"
        assert entities[0]['label'] == "ORG"
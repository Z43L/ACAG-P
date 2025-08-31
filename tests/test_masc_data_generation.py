import pytest
from unittest.mock import Mock, patch
from src.masc.data_generator import SyntheticDataGenerator

class TestSyntheticDataGenerator:
    """Pruebas para el generador de datos sintéticos"""
    
    @patch('transformers.pipeline')
    def test_generator_initialization(self, mock_pipeline):
        """Prueba inicialización del generador"""
        mock_ncd = Mock()
        mock_pipeline.return_value = Mock()
        
        generator = SyntheticDataGenerator(mock_ncd, "question-model")
        assert generator.ncd_client is not None
        assert generator.question_generator is not None
    
    def test_qa_pair_generation(self):
        """Prueba generación de pares pregunta-respuesta"""
        mock_ncd = Mock()
        generator = SyntheticDataGenerator(mock_ncd)
        
        knowledge_chunk = {
            'text': 'La inteligencia artificial es el campo de estudio que se enfoca en crear sistemas que pueden aprender y razonar como humanos.',
            'metadata': {'source': 'test'}
        }
        
        qa_pairs = generator.generate_qa_pairs(knowledge_chunk, num_questions=2)
        
        assert len(qa_pairs) == 2
        for qa_pair in qa_pairs:
            assert 'question' in qa_pair
            assert 'answer' in qa_pair
            assert qa_pair['answer'] == knowledge_chunk['text']
            assert 'metadata' in qa_pair
    
    @patch('transformers.pipeline')
    def test_question_generation_with_model(self, mock_pipeline):
        """Prueba generación de preguntas usando modelo"""
        mock_ncd = Mock()
        mock_generator = Mock()
        mock_generator.return_value = [{'generated_text': '¿Qué es la inteligencia artificial?\n¿Cómo funciona?'}]
        mock_pipeline.return_value = mock_generator
        
        generator = SyntheticDataGenerator(mock_ncd)
        questions = generator._generate_questions("Texto sobre inteligencia artificial", 2)
        
        assert len(questions) == 2
        assert all(q.endswith('?') for q in questions)
        mock_generator.assert_called_once()
    
    def test_conversation_training_data(self):
        """Prueba generación de datos de entrenamiento desde conversaciones"""
        mock_ncd = Mock()
        generator = SyntheticDataGenerator(mock_ncd)
        
        conversations = [
            {'query': '¿Qué es AI?', 'response': 'La inteligencia artificial es...', 'timestamp': '2023-01-01'},
            {'query': '¿Cómo se usa?', 'response': 'Se usa en muchos campos...', 'timestamp': '2023-01-01'}
        ]
        
        training_data = generator.generate_from_conversations(conversations, num_samples=2)
        
        assert len(training_data) == 2
        for item in training_data:
            assert 'instruction' in item
            assert 'output' in item
            assert item['source'] == 'conversation'
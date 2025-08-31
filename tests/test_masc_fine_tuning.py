import pytest
from unittest.mock import Mock, patch
from src.masc.fine_tuner import QLoRATrainer

class TestQLoRATrainer:
    """Pruebas para el fine-tuning con QLoRA"""
    
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForCausalLM.from_pretrained')
    @patch('peft.prepare_model_for_kbit_training')
    @patch('peft.get_peft_model')
    def test_model_preparation(self, mock_get_peft, mock_prepare, mock_model, mock_tokenizer):
        """Prueba preparación del modelo para QLoRA"""
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        mock_prepare.return_value = Mock()
        mock_get_peft.return_value = Mock()
        
        trainer = QLoRATrainer("test-model")
        model = trainer.prepare_model()
        
        assert model is not None
        mock_tokenizer.assert_called_once()
        mock_model.assert_called_once()
    
    def test_dataset_preparation(self):
        """Prueba preparación del dataset de entrenamiento"""
        trainer = QLoRATrainer("test-model")
        
        training_data = [
            {'instruction': '¿Qué es AI?', 'output': 'La inteligencia artificial es...'},
            {'question': '¿Cómo funciona?', 'answer': 'Funciona mediante...'}
        ]
        
        dataset = trainer.prepare_dataset(training_data)
        
        assert len(dataset) == 2
        # Verificar que se formateó correctamente
        assert any('### Instruction:' in item['text'] for item in dataset)
        assert any('Question:' in item['text'] for item in dataset)
    
    @patch('transformers.AutoTokenizer.from_pretrained')
    @patch('transformers.AutoModelForCausalLM.from_pretrained')
    @patch('peft.prepare_model_for_kbit_training')
    @patch('peft.get_peft_model')
    @patch('transformers.TrainingArguments')
    @patch('transformers.Trainer')
    def test_training_process(self, mock_trainer, mock_args, mock_get_peft, 
                            mock_prepare, mock_model, mock_tokenizer):
        """Prueba proceso completo de training"""
        # Configurar mocks
        mock_tokenizer.return_value = Mock()
        mock_model.return_value = Mock()
        mock_prepare.return_value = Mock()
        mock_get_peft.return_value = Mock()
        mock_args_instance = Mock()
        mock_args.return_value = mock_args_instance
        mock_trainer_instance = Mock()
        mock_trainer.return_value = mock_trainer_instance
        
        trainer = QLoRATrainer("test-model")
        
        training_data = [
            {'instruction': 'Test', 'output': 'Test response'}
        ]
        
        model_path = trainer.train(training_data, num_epochs=1, batch_size=1)
        
        assert model_path is not None
        mock_trainer_instance.train.assert_called_once()
        mock_trainer_instance.save_model.assert_called_once()
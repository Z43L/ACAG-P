from typing import Dict, List, Any
import random
from transformers import pipeline
import re

class SyntheticDataGenerator:
    """Genera datos de entrenamiento sintéticos para fine-tuning continuo"""
    
    def __init__(self, ncd_client, question_generator_model: str = "microsoft/DialoGPT-medium"):
        self.ncd_client = ncd_client
        self.question_generator = pipeline(
            "text2text-generation",
            model=question_generator_model,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
    
    def generate_qa_pairs(self, knowledge_chunk: Dict[str, Any], num_questions: int = 3) -> List[Dict]:
        """Genera pares pregunta-respuesta a partir de fragmentos de conocimiento"""
        text = knowledge_chunk.get('text', '')
        metadata = knowledge_chunk.get('metadata', {})
        
        if not text or len(text.split()) < 10:
            return []
        
        questions = self._generate_questions(text, num_questions)
        
        qa_pairs = []
        for question in questions:
            qa_pairs.append({
                'question': question,
                'answer': text,
                'context': text,
                'metadata': {
                    **metadata,
                    'source': 'synthetic',
                    'confidence': 0.8
                }
            })
        
        return qa_pairs
    
    def generate_from_conversations(self, conversations: List[Dict], num_samples: int = 5) -> List[Dict]:
        """Genera datos de entrenamiento a partir de conversaciones reales"""
        training_data = []
        
        for conv in conversations:
            if 'query' in conv and 'response' in conv:
                training_data.append({
                    'instruction': conv['query'],
                    'input': '',
                    'output': conv['response'],
                    'source': 'conversation',
                    'metadata': conv.get('metadata', {})
                })
        
        return training_data[:num_samples]
    
    def _generate_questions(self, text: str, num_questions: int) -> List[str]:
        """Genera preguntas relevantes usando modelo de generación"""
        prompt = f"""
        Basado en el siguiente texto, genera {num_questions} preguntas relevantes y variadas:
        
        Texto: {text}
        
        Preguntas:
        """
        
        try:
            response = self.question_generator(
                prompt,
                max_length=100,
                num_return_sequences=1,
                temperature=0.8,
                do_sample=True
            )
            
            generated_text = response[0]['generated_text']
            questions = [q.strip() for q in generated_text.split('\n') if q.strip()]
            return questions[:num_questions]
            
        except Exception:
            return self._fallback_question_generation(text, num_questions)
    
    def _fallback_question_generation(self, text: str, num_questions: int) -> List[str]:
        """Método de fallback para generación de preguntas"""
        sentences = re.split(r'[.!?]+', text)
        questions = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 5 and len(questions) < num_questions:
                # Transformaciones básicas a preguntas
                if sentence.startswith(('The ', 'A ', 'An ')):
                    question = "What is " + sentence.lower()
                elif re.match(r'^[A-Z][a-z]+', sentence):
                    question = "Who is " + sentence
                else:
                    question = "What is " + sentence
                
                questions.append(question + "?")
        
        return questions
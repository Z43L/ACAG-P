from typing import Dict, List, Any, Optional
from transformers import pipeline
import logging
from datetime import datetime, timedelta

class SyntheticDataGenerator:
    """Genera datos de entrenamiento sintéticos a partir del conocimiento"""
    
    def __init__(self, ncd_client, question_model: str = "microsoft/DialoGPT-medium"):
        self.ncd_client = ncd_client
        self.question_generator = pipeline(
            "text2text-generation",
            model=question_model,
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        self.logger = logging.getLogger(__name__)
        
    def generate_qa_pairs(self, knowledge_chunk: Dict[str, Any], 
                         num_questions: int = 3) -> List[Dict]:
        """Genera pares pregunta-respuesta a partir de un fragmento de conocimiento"""
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
                    'generated_at': datetime.now().isoformat(),
                    'source': 'synthetic',
                    'confidence': 0.8
                }
            })
            
        return qa_pairs
        
    def generate_from_conversations(self, conversations: List[Dict], 
                                  num_samples: int = 5) -> List[Dict]:
        """Genera datos de entrenamiento a partir de conversaciones"""
        training_data = []
        
        for conv in conversations:
            if 'query' in conv and 'response' in conv:
                training_data.append({
                    'instruction': conv['query'],
                    'input': '',
                    'output': conv['response'],
                    'source': 'conversation',
                    'metadata': {
                        'timestamp': conv.get('timestamp'),
                        'user_id': conv.get('user_id'),
                        'confidence': 0.9
                    }
                })
                
        return training_data[:num_samples]
        
    def _generate_questions(self, text: str, num_questions: int) -> List[str]:
        """Genera preguntas relevantes para el texto usando modelo de generación"""
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
            
        except Exception as e:
            self.logger.warning(f"Error generando preguntas, usando fallback: {str(e)}")
            return self._fallback_question_generation(text, num_questions)
            
    def _fallback_question_generation(self, text: str, num_questions: int) -> List[str]:
        """Generación de preguntas de fallback usando métodos heurísticos"""
        import re
        
        questions = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence.split()) > 5 and len(questions) < num_questions:
                # Simple transformación a pregunta
                if sentence.startswith(('The ', 'A ', 'An ')):
                    question = "What is " + sentence.lower()
                elif re.match(r'^[A-Z][a-z]+', sentence):
                    question = "Who is " + sentence
                else:
                    question = "What is " + sentence
                    
                questions.append(question + "?")
                
        return questions
        
    def get_new_knowledge(self, since: datetime) -> List[Dict]:
        """Obtiene conocimiento nuevo desde el timestamp especificado"""
        # Implementación específica para consultar el NCD
        query = """
        MATCH (d:Document)
        WHERE d.timestamp > $since
        RETURN d.text AS text, d.metadata AS metadata
        ORDER BY d.timestamp DESC
        LIMIT 100
        """
        
        try:
            results = self.ncd_client.execute_cypher(query, {'since': since.isoformat()})
            return [{'text': r['text'], 'metadata': r['metadata']} for r in results]
        except Exception as e:
            self.logger.error(f"Error obteniendo nuevo conocimiento: {str(e)}")
            return []
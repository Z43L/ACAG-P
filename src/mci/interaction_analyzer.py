from typing import Dict, List, Any
from textblob import TextBlob
import re
from datetime import datetime
import logging

class InteractionAnalyzer:
    """Analiza interacciones para extraer información personal y relacional"""
    
    def __init__(self):
        self.patterns = {
            'name': re.compile(r'(my name is|I am|call me) ([A-Z][a-z]+)'),
            'preference': re.compile(r'(I like|I love|I enjoy|I prefer) ([^\.\?\!]+)'),
            'dislike': re.compile(r'(I hate|I dislike|I don\'t like) ([^\.\?\!]+)'),
            'fact': re.compile(r'(I was born|I live in|I work as|I study) ([^\.\?\!]+)')
        }
        self.logger = logging.getLogger(__name__)
        
    def analyze_interaction(self, user_id: str, query: str, response: str) -> Dict[str, Any]:
        """Analiza una interacción completa y extrae información relevante"""
        timestamp = datetime.now().isoformat()
        
        analysis = {
            'user_id': user_id,
            'timestamp': timestamp,
            'query': query,
            'response': response,
            'sentiment': self._analyze_sentiment(query, response),
            'personal_info': self._extract_personal_info(query),
            'preferences': self._extract_preferences(query),
            'importance': self._calculate_importance(query, response),
            'topics': self._extract_topics(query),
            'metadata': {
                'query_length': len(query),
                'response_length': len(response),
                'response_time_ms': None  # Se poblará posteriormente
            }
        }
        
        return analysis
        
    def _analyze_sentiment(self, query: str, response: str) -> Dict[str, float]:
        """Analiza el sentimiento de la interacción usando TextBlob"""
        query_blob = TextBlob(query)
        response_blob = TextBlob(response)
        
        return {
            'query_polarity': query_blob.sentiment.polarity,
            'query_subjectivity': query_blob.sentiment.subjectivity,
            'response_polarity': response_blob.sentiment.polarity,
            'response_subjectivity': response_blob.sentiment.subjectivity,
            'interaction_balance': (query_blob.sentiment.polarity + 
                                  response_blob.sentiment.polarity) / 2
        }
        
    def _extract_personal_info(self, query: str) -> Dict[str, Any]:
        """Extrae información personal del usuario de la consulta"""
        info = {}
        
        # Detección de nombre
        name_match = self.patterns['name'].search(query.lower())
        if name_match:
            info['possible_name'] = name_match.group(2)
            
        # Detección de datos factuales
        for fact_type, pattern in self.patterns.items():
            if fact_type in ['fact']:
                matches = pattern.findall(query.lower())
                for match in matches:
                    info[fact_type] = match[1].strip()
                    
        return info
        
    def _extract_preferences(self, query: str) -> Dict[str, List[str]]:
        """Extrae preferencias y dislikes del usuario"""
        preferences = {'likes': [], 'dislikes': []}
        
        # Preferencias positivas
        like_matches = self.patterns['preference'].findall(query.lower())
        for match in like_matches:
            preferences['likes'].append(match[1].strip())
            
        # Preferencias negativas
        dislike_matches = self.patterns['dislike'].findall(query.lower())
        for match in dislike_matches:
            preferences['dislikes'].append(match[1].strip())
            
        return preferences
        
    def _extract_topics(self, query: str) -> List[str]:
        """Extrae temas principales de la consulta"""
        # Implementación simplificada - en producción usaríamos NLP más avanzado
        topics = []
        common_topics = ['technology', 'science', 'sports', 'music', 'movies', 
                        'books', 'travel', 'food', 'health', 'education']
        
        query_lower = query.lower()
        for topic in common_topics:
            if topic in query_lower:
                topics.append(topic)
                
        return topics
        
    def _calculate_importance(self, query: str, response: str) -> float:
        """Calcula la importancia de la interacción basado en múltiples factores"""
        factors = {
            'query_complexity': min(len(query.split()) / 20, 1.0),
            'personal_references': self._count_personal_references(query) / 5,
            'emotional_content': self._count_emotional_words(query) / 3,
            'response_effort': min(len(response.split()) / 50, 1.0)
        }
        
        weights = {
            'query_complexity': 0.2,
            'personal_references': 0.3,
            'emotional_content': 0.3,
            'response_effort': 0.2
        }
        
        importance = sum(factors[factor] * weights[factor] for factor in factors)
        return min(importance, 1.0)
        
    def _count_personal_references(self, text: str) -> int:
        """Cuenta referencias personales en el texto"""
        personal_pronouns = [' I ', ' me ', ' my ', ' mine ', ' myself ']
        count = 0
        text_lower = f" {text.lower()} "
        
        for pronoun in personal_pronouns:
            count += text_lower.count(pronoun)
            
        return count
        
    def _count_emotional_words(self, text: str) -> int:
        """Cuenta palabras emocionales en el texto"""
        emotional_words = ['love', 'hate', 'happy', 'sad', 'angry', 'excited', 
                          'wonderful', 'terrible', 'awesome', 'awful', 'amazing']
        count = 0
        text_lower = text.lower()
        
        for word in emotional_words:
            count += text_lower.count(word)
            
        return count
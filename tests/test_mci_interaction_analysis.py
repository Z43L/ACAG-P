import pytest
from src.mci.interaction_analyzer import InteractionAnalyzer

class TestInteractionAnalyzer:
    """Pruebas para el analizador de interacciones del MCI"""
    
    def setUp(self):
        self.analyzer = InteractionAnalyzer()
    
    def test_sentiment_analysis(self):
        """Prueba análisis de sentimiento"""
        query = "Estoy muy contento con este sistema, es realmente útil"
        response = "Me alegra que te guste, seguiré mejorando"
        
        sentiment = self.analyzer._analyze_sentiment(query, response)
        
        assert 'query_polarity' in sentiment
        assert 'response_polarity' in sentiment
        assert 'interaction_balance' in sentiment
        
        # Debería detectar sentimiento positivo
        assert sentiment['interaction_balance'] > 0
    
    def test_personal_info_extraction(self):
        """Prueba extracción de información personal"""
        query = "Hola, me llamo Juan Pérez y tengo 30 años"
        
        personal_info = self.analyzer._extract_personal_info(query)
        
        assert 'possible_name' in personal_info
        assert personal_info['possible_name'] == 'Juan'
    
    def test_preference_extraction(self):
        """Prueba extracción de preferencias"""
        query = "Me gusta la música rock y el cine, pero no me gusta el deporte"
        
        preferences = self.analyzer._extract_preferences(query)
        
        assert 'likes' in preferences
        assert 'dislikes' in preferences
        assert 'música rock' in preferences['likes']
        assert 'deporte' in preferences['dislikes']
    
    def test_importance_calculation(self):
        """Prueba cálculo de importancia de interacción"""
        query = "Este es un mensaje personal muy importante para mí"
        response = "Una respuesta bastante detallada y significativa"
        
        importance = self.analyzer._calculate_importance(query, response)
        
        assert 0 <= importance <= 1
        # Debería ser alta por el contenido personal y emocional
        assert importance > 0.5
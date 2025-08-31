from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np

class MemoryPersonalityManager:
    """Gestiona la memoria a largo plazo y la personalidad emergente"""
    
    def __init__(self, ncd_client):
        self.ncd_client = ncd_client
        self.user_profiles = {}
        self.interaction_history = {}
        
    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]):
        """Actualiza el perfil del usuario basado en la interacción"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = self._create_empty_profile(user_id)
            
        profile = self.user_profiles[user_id]
        
        # Actualizar información personal
        personal_info = interaction_data.get('personal_info', {})
        if 'possible_name' in personal_info:
            profile['personal_info']['name'] = personal_info['possible_name']
            
        # Actualizar preferencias
        preferences = interaction_data.get('preferences', {})
        for like in preferences.get('likes', []):
            if like not in profile['preferences']['likes']:
                profile['preferences']['likes'].append(like)
                
        for dislike in preferences.get('dislikes', []):
            if dislike not in profile['preferences']['dislikes']:
                profile['preferences']['dislikes'].append(dislike)
                
        # Actualizar estadísticas de interacción
        profile['interaction_stats']['total_interactions'] += 1
        profile['interaction_stats']['last_interaction'] = interaction_data['timestamp']
        
        # Calcular engagement score
        profile['engagement_score'] = self._calculate_engagement_score(user_id)
        
        # Guardar en NCD
        self._save_profile_to_ncd(profile)
        
    def update_system_personality(self, interaction_data: Dict[str, Any]):
        """Actualiza la personalidad del sistema basado en interacciones"""
        # La personalidad emerge de los patrones de interacción
        # Implementación simplificada - en producción sería más compleja
        
        # Extraer características del estilo de respuesta
        response_style = self._analyze_response_style(interaction_data['response'])
        
        # Actualizar tendencias de personalidad
        # (esto sería mucho más sofisticado en implementación real)
        personality_traits = self._get_personality_traits()
        
        # Ajustar traits basado en la interacción
        # Por ejemplo, respuestas más largas podrían indicar mayor extraversión
        response_length = len(interaction_data['response'])
        if response_length > 100:
            personality_traits['extraversion'] = min(personality_traits['extraversion'] + 0.01, 1.0)
            
        # Guardar traits actualizados
        self._save_personality_traits(personality_traits)
        
    def add_to_memory(self, user_id: str, interaction_data: Dict[str, Any]):
        """Añade la interacción a la memoria"""
        memory_entry = {
            'type': 'interaction',
            'content': {
                'query': interaction_data['query'],
                'response': interaction_data['response']
            },
            'metadata': {
                'timestamp': interaction_data['timestamp'],
                'importance': interaction_data['importance'],
                'sentiment': interaction_data['sentiment']
            },
            'user_id': user_id
        }
        
        # Almacenar en memoria a corto plazo (cache)
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
            
        self.interaction_history[user_id].append(memoryentry)
        
        # Si es importante, almacenar en memoria a largo plazo (NCD)
        if interaction_data['importance'] > 0.7:
            self._save_to_long_term_memory(memory_entry)
            
    def get_context_for_user(self, user_id: str, max_items: int = 10) -> List[Dict]:
        """Obtiene contexto relevante para un usuario"""
        context = []
        
        # Memoria a corto plazo (interacciones recientes)
        recent_interactions = self.interaction_history.get(user_id, [])
        context.extend(recent_interactions[-max_items:])
        
        # Perfil del usuario
        if user_id in self.user_profiles:
            context.append({
                'type': 'profile',
                'content': self.user_profiles[user_id],
                'metadata': {'source': 'user_profile'}
            })
            
        return context
        
    def _create_empty_profile(self, user_id: str) -> Dict[str, Any]:
        """Crea un perfil vacío para un nuevo usuario"""
        return {
            'user_id': user_id,
            'personal_info': {
                'name': None,
                'estimated_age': None,
                'estimated_interests': []
            },
            'preferences': {
                'likes': [],
                'dislikes': []
            },
            'interaction_stats': {
                'total_interactions': 0,
                'first_interaction': datetime.now().isoformat(),
                'last_interaction': None,
                'average_response_length': 0
            },
            'engagement_score': 0.5  # Neutral por defecto
        }
        
    def _calculate_engagement_score(self, user_id: str) -> float:
        """Calcula el score de engagement del usuario"""
        profile = self.user_profiles[user_id]
        stats = profile['interaction_stats']
        
        # Factores para engagement score
        factors = {
            'interaction_frequency': min(stats['total_interactions'] / 100, 1.0),
            'recency': self._calculate_recency_score(stats['last_interaction']),
            'response_ratio': 0.5  # Placeholder - necesitaríamos más datos
        }
        
        # Ponderación
        weights = {
            'interaction_frequency': 0.4,
            'recency': 0.4,
            'response_ratio': 0.2
       }
        
        return sum(factors[factor] * weights[factor] for factor in factors)
        
    def _calculate_recency_score(self, last_interaction: str) -> float:
        """Calcula score basado en la recencia de la interacción"""
        if not last_interaction:
            return 0.0
            
        last_time = datetime.fromisoformat(last_interaction)
        time_diff = datetime.now() - last_time
        
        # Score decae exponencialmente con el tiempo
        # 50% de decay después de 7 días
        decay_rate = 0.099  # Ajustado para half-life de 7 días
        return np.exp(-decay_rate * time_diff.days)
        
    def _analyze_response_style(self, response: str) -> Dict[str, Any]:
        """Analiza el estilo de la respuesta"""
        # Implementación simplificada
        return {
            'length': len(response),
            'complexity': len(response.split()) / len(response.split('.')),
            'formality': self._estimate_formality(response)
        }
        
    def _estimate_formality(self, text: str) -> float:
        """Estima el nivel de formalidad del texto"""
        formal_words = ['therefore', 'however', 'furthermore', 'thus', 'hence']
        informal_words = ['hey', 'cool', 'awesome', 'lol', 'omg']
        
        formal_count = sum(1 for word in formal_words if word in text.lower())
        informal_count = sum(1 for word in informal_words if word in text.lower())
        
        total = formal_count + informal_count
        if total == 0:
            return 0.5
            
        return formal_count / total
        
    def _get_personality_traits(self) -> Dict[str, float]:
        """Obtiene los traits de personalidad actuales"""
        # En producción, esto vendría del NCD
        return {
            'openness': 0.5,
            'conscientiousness': 0.5,
            'extraversion': 0.5,
            'agreeableness': 0.5,
            'neuroticism': 0.5
        }
        
    def _save_profile_to_ncd(self, profile: Dict[str, Any]):
        """Guarda el perfil en el NCD"""
        # Implementación específica dependiendo del schema del NCD
        pass
        
    def _save_personality_traits(self, traits: Dict[str, float]):
        """Guarda los traits de personalidad en el NCD"""
        # Implementación específica
        pass
        
    def _save_to_long_term_memory(self, memory_entry: Dict[str, Any]):
        """Guarda en memoria a largo plazo (NCD)"""
        # Implementación específica
        pass
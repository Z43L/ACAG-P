from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from dataclasses import dataclass
from enum import Enum
import os

class PersonalityTrait(Enum):
    """Rasgos de personalidad basados en el modelo Big Five"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"

@dataclass
class UserProfile:
    """Estructura de datos para el perfil de usuario"""
    user_id: str
    personal_info: Dict[str, Any]
    preferences: Dict[str, List[str]]
    interaction_stats: Dict[str, int]
    relationship_level: float  # 0.0 to 1.0
    created_at: datetime
    updated_at: datetime

@dataclass
class SystemPersonality:
    """Estructura de datos para la personalidad del sistema"""
    traits: Dict[PersonalityTrait, float]  # 0.0 to 1.0 for each trait
    communication_style: Dict[str, float]
    developed_at: datetime
    last_adapted: datetime

class ProfileManager:
    """Gestiona perfiles de usuario y la personalidad del sistema"""
    
    def __init__(self, storage_path: str = "./data/profiles"):
        self.storage_path = storage_path
        self.user_profiles: Dict[str, UserProfile] = {}
        self.system_personality: Optional[SystemPersonality] = None
        self.logger = logging.getLogger(__name__)
        
        self._load_profiles()
        self._initialize_system_personality()
        
    def _load_profiles(self) -> None:
        """Carga perfiles de usuario desde almacenamiento persistente"""
        try:
            profiles_file = f"{self.storage_path}/user_profiles.json"
            if os.path.exists(profiles_file):
                with open(profiles_file, 'r') as f:
                    profiles_data = json.load(f)
                    
                for user_id, profile_data in profiles_data.items():
                    # Convertir strings de fecha a objetos datetime
                    profile_data['created_at'] = datetime.fromisoformat(profile_data['created_at'])
                    profile_data['updated_at'] = datetime.fromisoformat(profile_data['updated_at'])
                    self.user_profiles[user_id] = UserProfile(**profile_data)
                    
        except Exception as e:
            self.logger.error(f"Error loading profiles: {str(e)}")
            
    def _initialize_system_personality(self) -> None:
        """Inicializa la personalidad del sistema con valores por defecto"""
        default_traits = {
            PersonalityTrait.OPENNESS: 0.7,
            PersonalityTrait.CONSCIENTIOUSNESS: 0.6,
            PersonalityTrait.EXTRAVERSION: 0.5,
            PersonalityTrait.AGREEABLENESS: 0.8,
            PersonalityTrait.NEUROTICISM: 0.3
        }
        
        default_style = {
            'formality': 0.6,
            'warmth': 0.7,
            'humor': 0.4,
            'detail_level': 0.5
        }
        
        now = datetime.now()
        self.system_personality = SystemPersonality(
            traits=default_traits,
            communication_style=default_style,
            developed_at=now,
            last_adapted=now
        )
        
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Obtiene el perfil de un usuario, creándolo si no existe"""
        if user_id not in self.user_profiles:
            self._create_new_profile(user_id)
            
        return self.user_profiles[user_id]
        
    def _create_new_profile(self, user_id: str) -> None:
        """Crea un nuevo perfil de usuario"""
        now = datetime.now()
        new_profile = UserProfile(
            user_id=user_id,
            personal_info={},
            preferences={'likes': [], 'dislikes': []},
            interaction_stats={
                'total_interactions': 0,
                'sessions_count': 0,
                'avg_response_length': 0
            },
            relationship_level=0.1,  # Nivel inicial de relación
            created_at=now,
            updated_at=now
        )
        
        self.user_profiles[user_id] = new_profile
        self._save_profiles()
        
    def update_user_profile(self, user_id: str, interaction_analysis: Dict[str, Any]) -> None:
        """Actualiza el perfil de usuario basado en el análisis de interacción"""
        profile = self.get_user_profile(user_id)
        
        # Actualizar información personal
        personal_info = interaction_analysis.get('personal_info', {})
        for key, value in personal_info.items():
            if value:  # Solo actualizar si hay valor
                profile.personal_info[key] = value
                
        # Actualizar preferencias
        preferences = interaction_analysis.get('preferences', {})
        for like in preferences.get('likes', []):
            if like not in profile.preferences['likes']:
                profile.preferences['likes'].append(like)
                
        for dislike in preferences.get('dislikes', []):
            if dislike not in profile.preferences['dislikes']:
                profile.preferences['dislikes'].append(dislike)
                
        # Actualizar estadísticas
        profile.interaction_stats['total_interactions'] += 1
        profile.interaction_stats['avg_response_length'] = (
            (profile.interaction_stats['avg_response_length'] * 
             (profile.interaction_stats['total_interactions'] - 1) +
             interaction_analysis['metadata']['response_length']) /
            profile.interaction_stats['total_interactions']
        )
        
        # Actualizar nivel de relación (basado en importancia de interacción)
        importance = interaction_analysis.get('importance', 0.1)
        profile.relationship_level = min(1.0, profile.relationship_level + (importance * 0.1))
        
        profile.updated_at = datetime.now()
        self._save_profiles()
        
    def adapt_system_personality(self, interaction_analysis: Dict[str, Any]) -> None:
        """Adapta la personalidad del sistema basado en interacciones"""
        if not self.system_personality:
            return
            
        sentiment = interaction_analysis.get('sentiment', {})
        importance = interaction_analysis.get('importance', 0.1)
        
        # Ajustar traits basado en el sentimiento de la interacción
        balance = sentiment.get('interaction_balance', 0)
        
        # Lógica de adaptación simplificada
        if balance > 0.3:  # Interacción positiva
            self.system_personality.traits[PersonalityTrait.AGREEABLENESS] = min(
                1.0, self.system_personality.traits[PersonalityTrait.AGREEABLENESS] + 0.01
            )
        elif balance < -0.3:  # Interacción negativa
            self.system_personality.traits[PersonalityTrait.NEUROTICISM] = min(
                1.0, self.system_personality.traits[PersonalityTrait.NEUROTICISM] + 0.01
            )
            
        self.system_personality.last_adapted = datetime.now()
        
    def _save_profiles(self) -> None:
        """Guarda los perfiles en almacenamiento persistente"""
        try:
            os.makedirs(self.storage_path, exist_ok=True)
            
            # Convertir a formato serializable
            serializable_profiles = {}
            for user_id, profile in self.user_profiles.items():
                serializable_profiles[user_id] = {
                    'user_id': profile.user_id,
                    'personal_info': profile.personal_info,
                    'preferences': profile.preferences,
                    'interaction_stats': profile.interaction_stats,
                    'relationship_level': profile.relationship_level,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat()
                }
                
            with open(f"{self.storage_path}/user_profiles.json", 'w') as f:
                json.dump(serializable_profiles, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving profiles: {str(e)}")
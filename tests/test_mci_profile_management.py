import pytest
from datetime import datetime
from src.mci.profile_manager import ProfileManager, UserProfile

class TestProfileManager:
    """Pruebas para la gestión de perfiles del MCI"""
    
    def test_profile_creation(self):
        """Prueba creación de nuevo perfil"""
        manager = ProfileManager()
        user_id = "new_user_123"
        
        profile = manager.get_user_profile(user_id)
        
        assert profile.user_id == user_id
        assert profile.relationship_level == 0.1  # Nivel inicial
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)
    
    def test_profile_update(self):
        """Prueba actualización de perfil con análisis de interacción"""
        manager = ProfileManager()
        user_id = "test_user"
        
        analysis = {
            'personal_info': {'possible_name': 'Test'},
            'preferences': {
                'likes': ['tecnología', 'música'],
                'dislikes': ['deporte']
            },
            'importance': 0.8
        }
        
        manager.update_user_profile(user_id, analysis)
        profile = manager.get_user_profile(user_id)
        
        assert profile.personal_info['possible_name'] == 'Test'
        assert 'tecnología' in profile.preferences['likes']
        assert 'deporte' in profile.preferences['dislikes']
        assert profile.relationship_level > 0.1  # Debería haber aumentado
    
    def test_system_personality_adaptation(self):
        """Prueba adaptación de la personalidad del sistema"""
        manager = ProfileManager()
        
        # Interacción positiva
        analysis_positive = {
            'sentiment': {'interaction_balance': 0.7},
            'importance': 0.6
        }
        
        manager.adapt_system_personality(analysis_positive)
        
        # Verificar que los traits se adaptaron
        assert manager.system_personality is not None
        assert manager.system_personality.last_adapted > manager.system_personality.developed_at
    
    def test_profile_persistence(self):
        """Prueba persistencia de perfiles"""
        manager = ProfileManager()
        user_id = "persistent_user"
        
        # Crear y actualizar perfil
        analysis = {
            'personal_info': {'name': 'Persistent'},
            'preferences': {'likes': ['data']},
            'importance': 0.5
        }
        
        manager.update_user_profile(user_id, analysis)
        
        # Simular recreación del manager (como si se reiniciara)
        manager2 = ProfileManager()
        profile = manager2.get_user_profile(user_id)
        
        # Debería mantener los datos persistidos
        assert profile.personal_info.get('name') == 'Persistent'
        assert 'data' in profile.preferences['likes']
"""
Módulo de Conciencia Interpersonal (MCI) - ACAG-P
Sistema de gestión de identidad, relaciones y memoria personal
"""

from typing import Dict, Any, Optional
import logging
from .interaction_analyzer import InteractionAnalyzer
from .profile_manager import ProfileManager, MemoryType
from .memory_manager import MemoryManager

class InterpersonalAwarenessModule:
    """Módulo principal de conciencia interpersonal"""
    
    def __init__(self, ncd_client, art_client, config: Dict[str, Any] = None):
        self.ncd_client = ncd_client
        self.art_client = art_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Inicializar componentes
        self.interaction_analyzer = InteractionAnalyzer()
        self.profile_manager = ProfileManager()
        self.memory_manager = MemoryManager(ncd_client)
        
        self.initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el módulo MCI"""
        try:
            self.logger.info("Inicializando Módulo de Conciencia Interpersonal")
            
            # Verificar dependencias
            if not self.ncd_client:
                raise ValueError("NCD client no proporcionado")
                
            self.initialized = True
            self.logger.info("MCI inicializado correctamente")
            return True
            
        except Exception as e:
            self.logger.error(f"Error inicializando MCI: {str(e)}")
            self.initialized = False
            return False
            
    def process_interaction(self, user_id: str, query: str, response: str) -> Dict[str, Any]:
        """Procesa una interacción completa y actualiza el estado interpersonal"""
        if not self.initialized:
            raise RuntimeError("MCI no inicializado")
            
        try:
            # 1. Analizar la interacción
            analysis = self.interaction_analyzer.analyze_interaction(user_id, query, response)
            
            # 2. Actualizar perfil de usuario
            self.profile_manager.update_user_profile(user_id, analysis)
            
            # 3. Adaptar personalidad del sistema
            self.profile_manager.adapt_system_personality(analysis)
            
            # 4. Almacenar memorias relevantes
            if analysis['importance'] > 0.3:
                memory_id = self.memory_manager.add_memory(
                    user_id=user_id,
                    memory_type=self._determine_memory_type(analysis),
                    content={
                        'query': query,
                        'response': response,
                        'analysis': analysis
                    },
                    importance=analysis['importance']
                )
                analysis['memory_id'] = memory_id
                
            return {
                'analysis': analysis,
                'user_profile': self.profile_manager.get_user_profile(user_id),
                'system_personality': self.profile_manager.system_personality
            }
            
        except Exception as e:
            self.logger.error(f"Error procesando interacción: {str(e)}")
            return {'error': str(e)}
            
    def get_context_for_user(self, user_id: str, current_query: str) -> Dict[str, Any]:
        """Obtiene contexto relevante para un usuario y consulta específicos"""
        try:
            # Obtener perfil de usuario
            profile = self.profile_manager.get_user_profile(user_id)
            
            # Obtener memorias relevantes
            context = {'query': current_query, 'topics': self.interaction_analyzer._extract_topics(current_query)}
            memories = self.memory_manager.get_relevant_memories(user_id, context)
            
            # Obtener personalidad del sistema para adaptación de estilo
            system_personality = self.profile_manager.system_personality
            
            return {
                'user_profile': profile,
                'relevant_memories': memories,
                'system_personality': system_personality,
                'communication_style': self._determine_communication_style(profile, system_personality)
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo contexto: {str(e)}")
            return {}
            
    def _determine_memory_type(self, analysis: Dict[str, Any]) -> MemoryType:
        """Determina el tipo de memoria basado en el análisis"""
        if analysis.get('personal_info'):
            return MemoryType.FACTUAL
        elif analysis.get('preferences'):
            return MemoryType.PREFERENCE
        elif analysis.get('sentiment', {}).get('interaction_balance', 0) != 0:
            return MemoryType.EMOTIONAL
        else:
            return MemoryType.EXPERIENTIAL
            
    def _determine_communication_style(self, profile: Any, 
                                   system_personality: Any) -> Dict[str, float]:
        """Determina el estilo de comunicación apropiado para el usuario"""
        base_style = system_personality.communication_style.copy()
        
        # Adaptar basado en el nivel de relación
        relationship_level = profile.relationship_level
        
        # Usuarios con mayor relación reciben un estilo más cálido y personal
        if relationship_level > 0.7:
            base_style['warmth'] = min(1.0, base_style['warmth'] + 0.2)
            base_style['formality'] = max(0.0, base_style['formality'] - 0.1)
            base_style['humor'] = min(1.0, base_style['humor'] + 0.1)
            
        # Usuarios nuevos reciben un estilo más formal
        elif relationship_level < 0.3:
            base_style['formality'] = min(1.0, base_style['formality'] + 0.1)
            base_style['warmth'] = max(0.3, base_style['warmth'] - 0.1)
            
        return base_style
        
    def cleanup(self) -> None:
        """Tareas de limpieza y mantenimiento del MCI"""
        self.memory_manager.cleanup_short_term_memory()
        self.logger.info("Tareas de limpieza del MCI completadas")
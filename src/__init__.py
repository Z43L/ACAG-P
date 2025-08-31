"""
ACAG-P - Arquitectura Cognitiva Aumentada por Grafos - Personalizada
Sistema de inteligencia artificial de próxima generación con aprendizaje continuo.
"""

__version__ = "0.1.0"

# Exportar módulos principales
from src.miu import UniversalIngestionModule
from src.mpe import ProcessingStructuringModule
from src.ncd import DualKnowledgeCore
from src.art import ReasoningTaskAgent
from src.masc import AdaptationSynthesisModule
from src.mci import InterpersonalAwarenessModule

# Exportar utilidades comunes
from src.core.tech_stack import TechStack
from src.core.config import settings
from src.core.logging import setup_logging

def initialize_system() -> dict:
    """Inicializa todos los módulos del sistema ACAG-P"""
    modules = {
        'mi': UniversalIngestionModule(),
        'mpe': ProcessingStructuringModule(),
        'ncd': DualKnowledgeCore(),
        'art': ReasoningTaskAgent(),
        'masc': AdaptationSynthesisModule(),
        'mci': InterpersonalAwarenessModule()
    }
    
    # Configurar dependencias entre módulos
    modules['mpe'].set_dependencies(miu=modules['miu'])
    modules['ncd'].set_dependencies(mpe=modules['mpe'])
    modules['art'].set_dependencies(ncd=modules['ncd'])
    modules['masc'].set_dependencies(ncd=modules['ncd'], art=modules['art'])
    modules['mci'].set_dependencies(art=modules['art'], ncd=modules['ncd'])
    
    return modules
#!/usr/bin/env python3
"""
Ejemplo de uso del Módulo de Conciencia Interpersonal
"""

import sys
sys.path.append('../src')

from mci import InterpersonalAwarenessModule
from ncd import DualKnowledgeCore
from art import ReasoningTaskAgent

def main():
    # Inicializar dependencias
    ncd = DualKnowledgeCore()
    art = ReasoningTaskAgent(ncd, {})
    
    if not ncd.initialize() or not art.initialize():
        print("Error inicializando dependencias")
        return
        
    # Inicializar MCI
    mci = InterpersonalAwarenessModule(ncd, art)
    if not mci.initialize():
        print("Error inicializando MCI")
        return
        
    print("✅ MCI inicializado correctamente")
    
    # Simular interacciones
    user_id = "test_user_123"
    test_interactions = [
        {
            "query": "Hola, me llamo María y me encanta la ciencia ficción",
            "response": "Hola María, es un placer conocerte. La ciencia ficción es un género fascinante."
        },
        {
            "query": "¿Qué libros de ciencia ficción me recomiendas?",
            "response": "Te recomiendo 'Dune' de Frank Herbert y 'Fundación' de Isaac Asimov."
        },
        {
            "query": "No me gusta la música clásica, prefiero el rock",
            "response": "Entendido, el rock es un género muy diverso y emocionante."
        }
    ]
    
    for i, interaction in enumerate(test_interactions):
        print(f"\n🎯 Interacción {i + 1}:")
        print(f"Usuario: {interaction['query']}")
        print(f"Sistema: {interaction['response']}")
        
        # Procesar interacción
        result = mci.process_interaction(user_id, interaction['query'], interaction['response'])
        
        if 'analysis' in result:
            print(f"📊 Importancia: {result['analysis']['importance']:.2f}")
            print(f"😊 Sentimiento: {result['analysis']['sentiment']['interaction_balance']:.2f}")
            
    # Obtener contexto para una nueva consulta
    print(f"\n🔍 Obteniendo contexto para usuario {user_id}...")
    context = mci.get_context_for_user(user_id, "¿Qué películas de ciencia ficción me recomiendas?")
    
    print(f"💝 Nivel de relación: {context['user_profile'].relationship_level:.2f}")
    print(f"🎭 Estilo de comunicación: {context['communication_style']}")
    print(f"📝 Preferencias: {context['user_profile'].preferences}")
    
    # Limpieza
    mci.cleanup()
    ncd.close()
    print("✅ Ejemplo completado")

if __name__ == "__main__":
    main()
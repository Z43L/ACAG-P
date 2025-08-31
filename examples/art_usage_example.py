#!/usr/bin/env python3
"""
Ejemplo de uso del Agente de Razonamiento y Tareas
"""

import sys
sys.path.append('../src')

from art import ReasoningTaskAgent
from ncd import DualKnowledgeCore

def main():
    # Inicializar NCD primero
    ncd = DualKnowledgeCore()
    if not ncd.initialize():
        print("Error inicializando NCD")
        return
        
    # Configuración del ART
    art_config = {
        'local_model_path': './models/llama-7b-acag',
        'openrouter_api_key': 'your-openrouter-key-here'
    }
    
    # Inicializar ART
    art = ReasoningTaskAgent(ncd, art_config)
    if not art.initialize():
        print("Error inicializando ART")
        return
        
    print("✅ ART inicializado correctamente")
    
    # Ejemplo de consultas
    test_queries = [
        "¿Qué es la inteligencia artificial?",
        "Explícanme las diferencias entre machine learning y deep learning",
        "Escribe un poema sobre la tecnología"
    ]
    
    user_id = "test_user_123"
    
    for query in test_queries:
        print(f"\n🔍 Consulta: {query}")
        
        result = art.process_query(user_id, query)
        
        print(f"📝 Respuesta: {result['response'][:200]}...")
        print(f"📊 Metadatos: Modelo usado - {result['metadata']['model_used']}")
        print(f"   Validación: {result['metadata']['validation_result']['confidence']:.2f} de confianza")
        
    # Mostrar métricas de performance
    metrics = art.get_performance_metrics()
    print(f"\n📈 Métricas de performance: {metrics['cost_metrics']['daily_cost']:.4f} costo diario")
    
    # Limpiar contexto
    art.clear_user_context(user_id)
    print("🧹 Contexto de usuario limpiado")
    
    # Cerrar conexiones
    ncd.close()
    print("✅ Ejemplo completado")

if __name__ == "__main__":
    main()
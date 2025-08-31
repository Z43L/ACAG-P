#!/usr/bin/env python3
"""
Ejemplo de uso del Núcleo de Conocimiento Dual de ACAG-P
"""

import sys
sys.path.append('../src')

from ncd import DualKnowledgeCore
from datetime import datetime
import json

def main():
    # Inicializar NCD
    ncd = DualKnowledgeCore()
    
    if not ncd.initialize():
        print("Error inicializando NCD")
        return
        
    print("✅ NCD inicializado correctamente")
    print("Estado:", ncd.get_status())
    
    # Ejemplo: Procesar datos estructurados (grafo)
    graph_data = {
        "nodes": [
            {
                "id": "entity_1",
                "labels": ["Entity", "Person"],
                "name": "John Doe",
                "type": "Person",
                "attributes": {"age": 30, "occupation": "Engineer"}
            },
            {
                "id": "entity_2", 
                "labels": ["Entity", "Organization"],
                "name": "Tech Corp",
                "type": "Company"
            }
        ],
        "relationships": [
            {
                "source": "entity_1",
                "target": "entity_2",
                "type": "WORKS_FOR",
                "since": "2020-01-01"
            }
        ]
    }
    
    result = ncd.process_data({"graph_data": graph_data}, "structured")
    print("📊 Datos estructurados procesados:", result)
    
    # Ejemplo: Procesar datos semánticos (texto)
    text_data = {
        "processed_text": "La inteligencia artificial está transformando la forma en que las empresas operan y toman decisiones.",
        "metadata": {
            "source": "internal_document",
            "author": "AI Research Team",
            "publish_date": "2023-01-15"
        }
    }
    
    result = ncd.process_data(text_data, "semantic")
    print("📝 Datos semánticos procesados:", result)
    
    # Ejemplo: Consultas
    print("\n🔍 Ejecutando consultas...")
    
    # Consulta Cypher
    cypher_result = ncd.query("cypher", query="MATCH (n) RETURN count(n) AS node_count")
    print("Cypher result:", cypher_result)
    
    # Búsqueda semántica
    semantic_result = ncd.query("semantic", query="transformación digital empresas", top_k=3)
    print("Semantic search result:", semantic_result)
    
    # Búsqueda híbrida
    hybrid_result = ncd.query("hybrid", query="inteligencia artificial", top_k=2)
    print("Hybrid search result:", hybrid_result)
    
    # Estadísticas del sistema
    stats = ncd.query("stats")
    print("System stats:", stats)
    
    # Cerrar conexiones
    ncd.close()
    print("✅ Ejemplo completado")

if __name__ == "__main__":
    main()
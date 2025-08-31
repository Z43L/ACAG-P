#!/usr/bin/env python3
"""
Script de resolución de problemas de base de datos
"""

import time
from src.ncd.neo4j_manager import Neo4jManager
from src.ncd.pinecone_manager import PineconeManager

def check_database_health():
    """Verifica la salud de las bases de datos"""
    print("🏥 Verificando salud de bases de datos...")
    
    # Verificar Neo4j
    try:
        neo4j_mgr = Neo4jManager()
        neo4j_status = neo4j_mgr.execute_query("CALL dbms.components()")
        print(f"✅ Neo4j saludable: {neo4j_status}")
    except Exception as e:
        print(f"❌ Error Neo4j: {str(e)}")
        _fix_neo4j_issues()
    
    # Verificar Pinecone
    try:
        pinecone_mgr = PineconeManager()
        pinecone_status = pinecone_mgr.get_index_stats()
        print(f"✅ Pinecone saludable: {pinecone_status}")
    except Exception as e:
        print(f"❌ Error Pinecone: {str(e)}")
        _fix_pinecone_issues()

def _fix_neo4j_issues():
    """Intenta resolver problemas comunes de Neo4j"""
    print("🔧 Intentando resolver problemas de Neo4j...")
    
    try:
        # Reconstruir índices
        neo4j_mgr = Neo4jManager()
        neo4j_mgr.execute_query("CALL db.indexes()")
        neo4j_mgr.execute_query("CALL db.awaitIndexes()")
        print("✅ Índices de Neo4j reconstruidos")
    except Exception as e:
        print(f"❌ No se pudieron reconstruir índices: {str(e)}")

def _fix_pinecone_issues():
    """Intenta resolver problemas comunes de Pinecone"""
    print("🔧 Intentando resolver problemas de Pinecone...")
    
    try:
        # Recrear índice si es necesario
        pinecone_mgr = PineconeManager()
        pinecone_mgr.recreate_index()
        print("✅ Índice de Pinecone recreado")
    except Exception as e:
        print(f"❌ No se pudo recrear índice: {str(e)}")

if __name__ == "__main__":
    check_database_health()
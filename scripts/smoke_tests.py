#!/usr/bin/env python3
"""
Smoke tests para verificar el despliegue de ACAG-P
"""

import requests
import json
import sys
from datetime import datetime

def run_smoke_tests(base_url: str = "http://localhost:8000"):
    """Ejecuta tests de humo para verificar el despliegue"""
    tests = [
        test_health_endpoint,
        test_api_status,
        test_neo4j_connection,
        test_pinecone_connection,
        test_redis_connection,
        test_basic_query
    ]
    
    results = []
    for test in tests:
        try:
            result = test(base_url)
            results.append(result)
            print(f"✅ {test.__name__}: PASSED")
        except Exception as e:
            results.append({
                'test': test.__name__,
                'status': 'FAILED',
                'error': str(e)
            })
            print(f"❌ {test.__name__}: FAILED - {str(e)}")
    
    return results

def test_health_endpoint(base_url: str) -> dict:
    """Test del endpoint de health"""
    response = requests.get(f"{base_url}/health", timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if data['status'] != 'healthy':
        raise ValueError(f"Health status not healthy: {data['status']}")
    
    return {'test': 'health_endpoint', 'status': 'PASSED'}

def test_api_status(base_url: str) -> dict:
    """Test del estado de la API"""
    response = requests.get(f"{base_url}/api/status", timeout=10)
    response.raise_for_status()
    data = response.json()
    
    required_keys = ['version', 'environment', 'modules', 'timestamp']
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing key in status: {key}")
    
    return {'test': 'api_status', 'status': 'PASSED'}

def test_neo4j_connection(base_url: str) -> dict:
    """Test de conexión a Neo4j"""
    response = requests.get(f"{base_url}/api/database/neo4j/status", timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('connected', False):
        raise ValueError("Neo4j not connected")
    
    return {'test': 'neo4j_connection', 'status': 'PASSED'}

def test_pinecone_connection(base_url: str) -> dict:
    """Test de conexión a Pinecone"""
    response = requests.get(f"{base_url}/api/database/pinecone/status", timeout=15)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('connected', False):
        raise ValueError("Pinecone not connected")
    
    return {'test': 'pinecone_connection', 'status': 'PASSED'}

def test_redis_connection(base_url: str) -> dict:
    """Test de conexión a Redis"""
    response = requests.get(f"{base_url}/api/cache/status", timeout=10)
    response.raise_for_status()
    data = response.json()
    
    if not data.get('connected', False):
        raise ValueError("Redis not connected")
    
    return {'test': 'redis_connection', 'status': 'PASSED'}

def test_basic_query(base_url: str) -> dict:
    """Test de consulta básica"""
    test_query = {
        "query": "What is artificial intelligence?",
        "user_id": "smoke_test_user",
        "context": {}
    }
    
    response = requests.post(
        f"{base_url}/api/query",
        json=test_query,
        timeout=30
    )
    response.raise_for_status()
    data = response.json()
    
    if 'response' not in data:
        raise ValueError("No response in query result")
    
    return {'test': 'basic_query', 'status': 'PASSED'}

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"🚀 Ejecutando smoke tests contra {base_url}")
    print("=" * 50)
    
    results = run_smoke_tests(base_url)
    
    print("=" * 50)
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    total = len(results)
    
    print(f"📊 Resultados: {passed}/{total} tests pasados")
    
    if passed < total:
        print("❌ Smoke tests fallaron")
        sys.exit(1)
    else:
        print("✅ Todos los smoke tests pasaron")
        sys.exit(0)
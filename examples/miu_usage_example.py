#!/usr/bin/env python3
"""
Ejemplo de uso del Módulo de Ingesta Universal
"""

from src.miu import UniversalIngestionModule

def main():
    # Configuración del MIU
    config = {
        'adapters': {
            'text': {
                'encoding': 'utf-8'
            },
            'api': {
                'base_url': 'https://api.example.com',
                'timeout': 30,
                'headers': {
                    'Authorization': 'Bearer your-token-here'
                }
            },
            'database': {
                'connection_string': 'postgresql://user:password@localhost/db'
            }
        }
    }
    
    # Inicializar el módulo
    miu = UniversalIngestionModule(config)
    if not miu.initialize():
        print("Failed to initialize MIU")
        return
        
    print("MIU initialized successfully")
    print("Available adapters:", miu.get_status()['adapters_available'])
    
    # Ejemplo: Ingresar desde archivo de texto
    try:
        result = miu.ingest_data('text', {
            'path': '/path/to/your/document.txt'
        })
        print(result)
    except Exception as e:
        print(f"Text ingestion failed: {str(e)}")
        
    # Ejemplo: Ingresar desde API
    try:
        result = miu.ingest_data('api', {
            'endpoint': '/data/endpoint',
            'params': {'limit': 100}
        }, priority='high_priority')
        print(result)
    except Exception as e:
        print(f"API ingestion failed: {str(e)}")
        
    # Ejemplo: Ingresar desde base de datos
    try:
        result = miu.ingest_data('database', {
            'query': 'SELECT * FROM documents WHERE category = "technology"'
        })
        print(result)
    except Exception as e:
        print(f"Database ingestion failed: {str(e)}")
        
    # Mostrar estado final
    print("\nFinal status:")
    print(miu.get_status())

if __name__ == "__main__":
    main()
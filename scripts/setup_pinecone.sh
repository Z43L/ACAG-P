#!/bin/bash
# Configuración de entorno para Pinecone en ACAG-P

echo "Configurando Pinecone para ACAG-P..."

# Verificar variables de entorno requeridas
if [ -z "$PINECONE_API_KEY" ]; then
    echo "ERROR: PINECONE_API_KEY no está configurada"
    exit 1
fi

if [ -z "$PINECONE_ENVIRONMENT" ]; then
    echo "ERROR: PINECONE_ENVIRONMENT no está configurada"
    exit 1
fi

# Crear directorio de modelos de embeddings
mkdir -p models/embeddings

echo "Instalando dependencias de Pinecone..."
pip install pinecone-client sentence-transformers

echo "Verificando configuración..."
python -c "
import os
from src.ncd.pinecone_manager import PineconeManager

try:
    manager = PineconeManager(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT'),
        index_name='acag-knowledge'
    )
    print('✅ Pinecone configurado correctamente')
    print('Estadísticas del índice:', manager.get_index_stats())
except Exception as e:
    print('❌ Error configurando Pinecone:', str(e))
    exit(1)
"

echo "Configuración de Pinecone completada"
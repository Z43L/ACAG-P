#!/bin/bash
# Script de configuración de entorno para producción

set -a
source .env.production
set +a

# Crear directorios necesarios
mkdir -p ./data/{models,logs,backups}
mkdir -p ./config

# Configurar permisos
chmod 755 ./data
chmod 755 ./config

# Generar secrets si no existen
if [ ! -f .env.production ]; then
    cat > .env.production << EOF
# ACAG-P Production Environment
NEO4J_PASSWORD=$(openssl rand -base64 16)
REDIS_PASSWORD=$(openssl rand -base64 16)
JWT_SECRET=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# External Services
PINECONE_API_KEY=${PINECONE_API_KEY}
PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT}
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
MODEL_CACHE_SIZE=1000
EOF
fi

# Configurar Docker secrets
echo $NEO4J_PASSWORD > ./config/neo4j_password.txt
echo $REDIS_PASSWORD > ./config/redis_password.txt
chmod 600 ./config/*_password.txt
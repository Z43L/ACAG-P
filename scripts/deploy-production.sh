#!/bin/bash
# Script de despliegue automatizado para producción ACAG-P

set -e  # Exit on error

echo "🚀 Iniciando despliegue de ACAG-P a producción..."
DEPLOY_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/acag/deploy_${DEPLOY_TIMESTAMP}.log"

# Cargar variables de entorno
source .env.production

# Validaciones previas
echo "🔍 Realizando validaciones previas al despliegue..."
if [ -z "$NEOJ_PASSWORD" ]; then
    echo "❌ ERROR: NEO4J_PASSWORD no configurada" | tee -a $LOG_FILE
    exit 1
fi

if [ -z "$PINECONE_API_KEY" ]; then
    echo "❌ ERROR: PINECONE_API_KEY no configurada" | tee -a $LOG_FILE
    exit 1
fi

# Construir imágenes Docker
echo "📦 Construyendo imágenes Docker..." | tee -a $LOG_FILE
docker compose -f docker-compose.production.yml build >> $LOG_FILE 2>&1

# Verificar construcción
if [ $? -ne 0 ]; then
    echo "❌ Error construyendo imágenes Docker" | tee -a $LOG_FILE
    exit 1
fi

# Detener servicios existentes
echo "🛑 Deteniendo servicios existentes..." | tee -a $LOG_FILE
docker compose -f docker-compose.production.yml down >> $LOG_FILE 2>&1

# Desplegar nuevos servicios
echo "🔄 Desplegando servicios..." | tee -a $LOG_FILE
docker compose -f docker-compose.production.yml up -d >> $LOG_FILE 2>&1

# Esperar por servicios
echo "⏳ Esperando por servicios..." | tee -a $LOG_FILE
sleep 30

# Ejecutar health checks
echo "🏥 Ejecutando health checks..." | tee -a $LOG_FILE
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Despliegue exitoso. Todos los sistemas operativos." | tee -a $LOG_FILE
    
    # Ejecutar smoke tests
    echo "🧪 Ejecutando smoke tests..." | tee -a $LOG_FILE
    python scripts/smoke_tests.py >> $LOG_FILE 2>&1
    
    # Ejecutar migraciones de base de datos
    echo "🗄️ Ejecutando migraciones de base de datos..." | tee -a $LOG_FILE
    docker compose -f docker-compose.production.yml exec api python -m src.db.migrate >> $LOG_FILE 2>&1
    
    echo "🎉 Despliegue completado exitosamente a las $(date)" | tee -a $LOG_FILE
    
else
    echo "❌ ERROR: Health check falló. Status: $HEALTH_STATUS" | tee -a $LOG_FILE
    echo "📋 Revisando logs..." | tee -a $LOG_FILE
    docker compose -f docker-compose.production.yml logs >> $LOG_FILE 2>&1
    exit 1
fi
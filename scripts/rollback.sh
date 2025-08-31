#!/bin/bash
# Script de rollback para ACAG-P

set -e

echo "🔄 Iniciando proceso de rollback..."
ROLLBACK_TIMESTAMP=$(date +%Y%m%d_%M%S)
LOG_FILE="/var/log/acag/rollback_${ROLLBACK_TIMESTAMP}.log"

# Obtener versión anterior
PREVIOUS_VERSION=$(docker images --filter "reference=acag-api" --format "{{.Tag}}" | grep -v "latest" | sort -r | sed -n '2p')

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "❌ No se encontró versión anterior para rollback" | tee -a $LOG_FILE
    exit 1
fi

echo "⏪ Revertiendo a versión $PREVIOUS_VERSION..." | tee -a $LOG_FILE

# Detener servicios actuales
docker compose -f docker-compose.production.yml down >> $LOG_FILE 2>&1

# Taggear versión anterior como latest
docker tag acag-api:$PREVIOUS_VERSION acag-api:latest >> $LOG_FILE 2>&1

# Iniciar servicios con versión anterior
docker compose -f docker-compose.production.yml up -d >> $LOG_FILE 2>&1

# Verificar rollback
sleep 20
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_STATUS" = "200" ]; then
    echo "✅ Rollback exitoso a versión $PREVIOUS_VERSION" | tee -a $LOG_FILE
else
    echo "❌ Rollback falló. Health check: $HEALTH_STATUS" | tee -a $LOG_FILE
    exit 1
fi
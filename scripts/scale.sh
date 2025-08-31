#!/bin/bash
# Script de escalado para ACAG-P

SERVICE=$1
ACTION=$2
COUNT=$3

case "$ACTION" in
  "up")
    echo "📈 Escalando servicio $SERVICE a $COUNT instancias..."
    docker compose -f docker-compose.production.yml up -d --scale $SERVICE=$COUNT --no-recreate
    ;;
  "down")
    echo "📉 Reduciendo servicio $SERVICE a $COUNT instancias..."
    docker compose -f docker-compose.production.yml up -d --scale $SERVICE=$COUNT --no-recreate
    ;;
  *)
    echo "❌ Uso: scale.sh <service> <up|down> <count>"
    exit 1
    ;;
esac

# Esperar a que los servicios estén saludables
echo "⏳ Esperando por servicios..."
sleep 10

# Verificar estado
docker compose -f docker-compose.production.yml ps
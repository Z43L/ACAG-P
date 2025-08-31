#!/bin/bash
# Script de recovery para ACAG-P

set -e

if [ -z "$1" ]; then
    echo "❌ Especifica la ruta del archivo de backup"
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="/tmp/restore_$(date +%Y%m%d_%H%M%S)"

echo "🔄 Iniciando recovery desde $BACKUP_FILE..."
mkdir -p $RESTORE_DIR

# Extraer backup
echo "📦 Extrayendo backup..."
tar -xzf $BACKUP_FILE -C $RESTORE_DIR

# Detener servicios
echo "🛑 Deteniendo servicios..."
docker compose -f docker-compose.production.yml down

# Restaurar Neo4j
echo "🗄️ Restaurando Neo4j..."
docker run --rm \
  -v $RESTORE_DIR/neo4j:/backup \
  -v neo4j_data:/data \
  neo4j:5.12.0-enterprise \
  neo4j-admin restore --from=/backup --force

# Restaurar Redis
echo "🔴 Restaurando Redis..."
docker run --rm \
  -v $RESTORE_DIR/redis:/backup \
  -v redis_data:/data \
  redis:7.2-alpine \
  cp /backup/dump.rdb /data/

# Restaurar modelos y datos
echo "📁 Restaurando modelos y datos..."
rsync -av $RESTORE_DIR/models/ ./models/
rsync -av $RESTORE_DIR/data/ ./data/

# Iniciar servicios
echo "🚀 Iniciando servicios..."
docker compose -f docker-compose.production.yml up -d

# Limpiar
rm -rf $RESTORE_DIR

echo "✅ Recovery completado exitosamente"
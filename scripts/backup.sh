#!/bin/bash
# Script de backup para ACAG-P

set -e

BACKUP_DIR="/backups/acag"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

echo "💾 Iniciando backup de ACAG-P..."
mkdir -p $BACKUP_PATH

# Backup de Neo4j
echo "🗄️ Haciendo backup de Neo4j..."
docker exec acag-neo4j neo4j-admin backup --backup-dir=/tmp/backup --name=neo4j_backup
docker cp acag-neo4j:/tmp/backup $BACKUP_PATH/neo4j
docker exec acag-neo4j rm -rf /tmp/backup

# Backup de Redis
echo "🔴 Haciendo backup de Redis..."
docker exec acag-redis redis-cli SAVE
docker cp acag-redis:/data/dump.rdb $BACKUP_PATH/redis/
docker exec acag-redis redis-cli BGSAVE

# Backup de modelos
echo "🧠 Haciendo backup de modelos..."
rsync -av ./models/ $BACKUP_PATH/models/

# Backup de datos de aplicación
echo "📊 Haciendo backup de datos..."
rsync -av ./data/ $BACKUP_PATH/data/

# Crear archivo comprimido
echo "📦 Comprimiendo backup..."
tar -czf $BACKUP_PATH.tar.gz -C $BACKUP_PATH .

# Limpiar directorio temporal
rm -rf $BACKUP_PATH

# Rotar backups antiguos (mantener solo 7 días)
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $BACKUP_PATH.tar.gz"
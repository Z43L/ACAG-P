#!/bin/bash
# Rutina de mantenimiento diario para ACAG-P

echo "🔧 Iniciando rutina de mantenimiento diario..."
DATE=$(date +%Y%m%d)
LOG_FILE="/var/log/acag/maintenance_${DATE}.log"

# 1. Backup de bases de datos
echo "💾 Realizando backup de bases de datos..." | tee -a $LOG_FILE
docker exec acag-neo4j neo4j-admin backup --backup-dir=/backups --name=neo4j_backup_$DATE >> $LOG_FILE 2>&1

# 2. Limpieza de logs antiguos
echo "🧹 Limpiando logs antiguos..." | tee -a $LOG_FILE
find /var/log/acag -name "*.log" -mtime +30 -delete >> $LOG_FILE 2>&1

# 3. Limpieza de datos temporales
echo "🗑️ Limpiando datos temporales..." | tee -a $LOG_FILE
docker exec acag-api python -m src.core.cleanup --days 7 >> $LOG_FILE 2>&1

# 4. Verificación de integridad
echo "🔍 Verificando integridad del sistema..." | tee -a $LOG_FILE
docker exec acag-api python -m src.core.integrity_check >> $LOG_FILE 2>&1

# 5. Optimización de bases de datos
echo "⚡ Optimizando bases de datos..." | tee -a $LOG_FILE
docker exec acag-neo4j cypher-shell -u neo4j -p $NEO4J_PASSWORD "CALL db.indexes()" >> $LOG_FILE 2>&1

echo "✅ Rutina de mantenimiento completada" | tee -a $LOG_FILE
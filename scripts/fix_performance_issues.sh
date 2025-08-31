#!/bin/bash
# Script de resolución de problemas de rendimiento

echo "🔧 Resolviendo problemas de rendimiento..."

# 1. Verificar uso de recursos
echo "📊 Verificando uso de recursos..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
MEMORY_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')

echo "Uso de CPU: ${CPU_USAGE}%"
echo "Uso de memoria: ${MEMORY_USAGE}%"

# 2. Escalar servicios si es necesario
if (( $(echo "$CPU_USAGE > 85" | bc -l) )); then
    echo "⚡ Escalando servicios debido a alto uso de CPU..."
    docker-compose up -d --scale api=3 --scale worker=2
fi

# 3. Optimizar consultas a la base de datos
echo "🗄️ Optimizando consultas de base de datos..."
docker-compose exec neo4j cypher-shell "CALL db.indexes()"

# 4. Limpiar cache
echo "🧹 Limpiando cache..."
docker-compose exec redis redis-cli FLUSHALL

# 5. Revisar configuración
echo "🔍 Revisando configuración..."
python -c "
from src.core.config import settings
print(f'Configuración actual: {settings.dict()}')
"

echo "✅ Acciones de rendimiento completadas"
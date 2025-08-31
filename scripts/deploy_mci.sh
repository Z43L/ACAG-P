#!/bin/bash
# Script de despliegue del Módulo de Conciencia Interpersonal

echo "🚀 Desplegando Módulo de Conciencia Interpersonal..."

# Verificar dependencias
if [ -z "$NEO4J_URI" ]; then
    echo "❌ ERROR: NEO4J_URI no configurada"
    exit 1
fi

# Crear directorios de datos
mkdir -p data/profiles data/memories logs

# Instalar dependencias específicas del MCI
echo "📦 Instalando dependencias del MCI..."
pip install textblob python-dotenv

# Descargar datos de TextBlob
python -c "
import nltk
nltk.download('punkt')
nltk.download('brown')
nltk.download('movie_reviews')
print('✅ Datos de NLP descargados')
"

# Verificar configuración
echo "🔍 Verificando configuración..."
python -c "
from src.mci import InterpersonalAwarenessModule
from src.ncd import DualKnowledgeCore

ncd = DualKnowledgeCore('config/ncd_config.env')
if ncd.initialize():
    mci = InterpersonalAwarenessModule(ncd, None)
    if mci.initialize():
        print('✅ Configuración del MCI verificada correctamente')
    else:
        print('❌ Error inicializando MCI')
        exit(1)
else:
    print('❌ Error inicializando NCD')
    exit(1)
"

echo "✅ Despliegue del MCI completado exitosamente"
echo "📋 Próximos pasos:"
echo "   1. Verificar almacenamiento: ls -la data/"
echo "   2. Iniciar servicio: python -m src.mci.service"
echo "   3. Monitorear logs: tail -f /var/log/acag/mci.log"
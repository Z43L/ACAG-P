#!/bin/bash
# Script de despliegue del ART para ACAG-P

echo "🚀 Desplegando Agente de Razonamiento y Tareas..."

# Verificar variables de entorno requeridas
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ ERROR: OPENROUTER_API_KEY no configurada"
    exit 1
fi

if [ -z "$NEO4J_URI" ]; then
    echo "❌ ERROR: NEO4J_URI no configurada"
    exit 1
fi

# Crear directorios necesarios
mkdir -p models logs config

# Copiar configuración
cp ../config/art_config.yaml config/
cp ../config/ncd_config.env config/

# Instalar dependencias específicas del ART
echo "📦 Instalando dependencias del ART..."
pip install openai transformers torch sentencepiece

# Verificar que el modelo local existe
if [ ! -d "models/acag-local-model" ]; then
    echo "⚠️  Modelo local no encontrado, descargando..."
    python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('huggingface.co/models/acag-7b')
tokenizer = AutoTokenizer.from_pretrained('huggingface.co/models/acag-7b')
model.save_pretrained('./models/acag-local-model')
tokenizer.save_pretrained('./models/acag-local-model')
"
fi

# Verificar configuración
echo "🔍 Verificando configuración..."
python -c "
from src.art import ReasoningTaskAgent
from src.ncd import DualKnowledgeCore

ncd = DualKnowledgeCore('config/ncd_config.env')
if ncd.initialize():
    art = ReasoningTaskAgent(ncd, {
        'local_model_path': './models/acag-local-model',
        'openrouter_api_key': '$OPENROUTER_API_KEY'
    })
    if art.initialize():
        print('✅ Configuración verificada correctamente')
    else:
        print('❌ Error inicializando ART')
        exit(1)
else:
    print('❌ Error inicializando NCD')
    exit(1)
"

echo "✅ Despliegue del ART completado exitosamente"
echo "📋 Próximos pasos:"
echo "   1. Iniciar servicio: python -m src.art.service"
echo "   2. Verificar logs: tail -f /var/log/acag/art.log"
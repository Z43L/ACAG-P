#!/usr/bin/env python3
"""
Script de configuración del entorno de desarrollo para ACAG-P
"""

import subprocess
import sys
from pathlib import Path

def run_command(command: str, check: bool = True) -> bool:
    """Ejecuta un comando y muestra el output"""
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"Error ejecutando comando: {result.stderr}")
        return False
    
    return True

def setup_development_environment():
    """Configura el entorno completo de desarrollo"""
    
    # Verificar que Python 3.10+ está instalado
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 10):
        print("Se requiere Python 3.10 o superior")
        sys.exit(1)
    
    # Crear estructura de directorios
    directories = [
        "data/raw",
        "data/processed",
        "data/training",
        "models",
        "logs",
        "tests/data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Directorio creado: {directory}")
    
    # Instalar dependencias
    print("Instalando dependencias...")
    if not run_command("pip install -r requirements-dev.txt"):
        print("Error instalando dependencias de desarrollo")
        sys.exit(1)
    
    # Configurar pre-commit hooks
    print("Configurando pre-commit hooks...")
    if not run_command("pre-commit install"):
        print("Error configurando pre-commit")
        sys.exit(1)
    
    # Inicializar base de datos de prueba
    print("Inicializando bases de datos de prueba...")
    if not run_command("docker-compose up -d neo4j redis"):
        print("Error iniciando contenedores de prueba")
        sys.exit(1)
    
    print("✅ Entorno de desarrollo configurado exitosamente!")

if __name__ == "__main__":
    setup_development_environment()
import logging
import sys
from typing import Optional
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    module_name: Optional[str] = None
) -> logging.Logger:
    """
    Configura logging unificado para todos los módulos de ACAG-P
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Archivo donde escribir logs (opcional)
        module_name: Nombre del módulo para el logger
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(module_name or "acag-p")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Formato común
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
  # Handler para archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Loggers específicos por módulo
def get_modulelogger(module_name: str) -> logging.Logger:
    """Obtiene un logger específico para un módulo"""
    return setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=Path(f"logs/{module_name}.log"),
        module_name=f"acag-p.{module_name}"
    )
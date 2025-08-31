import logging
import json
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from datetime import datetime
import os

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configura el sistema de logging unificado para ACAG-P"""
    
    # Formateador JSON para logs estructurados
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super().add_fields(log_record, record, message_dict)
            log_record['timestamp'] = datetime.now().isoformat()
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['module'] = record.module
            log_record['function'] = record.funcName
            
    # Configurar logger principal
    logger = logging.getLogger('acag')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si se especifica)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        json_formatter = CustomJsonFormatter()
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    # Configurar loggers de terceros
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.INFO)
    
    return logger

def get_module_logger(module_name: str):
    """Obtiene un logger específico para un módulo"""
    return logging.getLogger(f'acag.{module_name}')
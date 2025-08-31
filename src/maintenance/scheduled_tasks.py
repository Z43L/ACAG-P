from typing import Dict, List, Any
from datetime import datetime, timedelta
import schedule
import time
import logging

class MaintenanceScheduler:
    """Programador de tareas de mantenimiento automatizado"""
    
    def __init__(self):
        self.tasks = []
        self.logger = logging.getLogger(__name__)
        
    def register_task(self, task_func, interval: str, **kwargs):
        """Registra una nueva tarea de mantenimiento"""
        task = {
            'function': task_func,
            'interval': interval,
            'kwargs': kwargs,
            'last_run': None,
            'next_run': self._calculate_next_run(interval)
        }
        self.tasks.append(task)
        
    def _calculate_next_run(self, interval: str) -> datetime:
        """Calcula la próxima ejecución basado en el intervalo"""
        now = datetime.now()
        
        if interval == 'hourly':
            return now + timedelta(hours=1)
        elif interval == 'daily':
            return now + timedelta(days=1)
        elif interval == 'weekly':
            return now + timedelta(weeks=1)
        elif interval.startswith('every_'):
            # Formato: every_X_[hours|days|weeks]
            parts = interval.split('_')
            if len(parts) == 3:
                amount = int(parts[1])
                unit = parts[2]
                if unit == 'hours':
                    return now + timedelta(hours=amount)
                elif unit == 'days':
                    return now + timedelta(days=amount)
                elif unit == 'weeks':
                    return now + timedelta(weeks=amount)
                    
        return now + timedelta(hours=1)  # Default
        
    def run_pending_tasks(self):
        """Ejecuta las tareas pendientes"""
        now = datetime.now()
        
        for task in self.tasks:
            if task['next_run'] <= now:
                try:
                    self.logger.info(f"Executing maintenance task: {task['function'].__name__}")
                    task['function'](**task['kwargs'])
                    task['last_run'] = now
                    task['next_run'] = self._calculate_next_run(task['interval'])
                except Exception as e:
                    self.logger.error(f"Error executing task {task['function'].__name__}: {str(e)}")
                    
    def start_scheduler(self):
        """Inicia el programador de mantenimiento"""
        self.logger.info("Starting maintenance scheduler")
        
        while True:
            self.run_pending_tasks()
            time.sleep(60)  # Check cada minuto

# Tareas de mantenimiento predefinidas
def cleanup_temp_files():
    """Limpia archivos temporales"""
    import tempfile
    import os
    import shutil
    
    temp_dir = tempfile.gettempdir()
    acag_temp_files = [f for f in os.listdir(temp_dir) if f.startswith('acag_')]
    
    for file in acag_temp_files:
        try:
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.warning(f"Error cleaning up temp file {file}: {str(e)}")

def optimize_databases():
    """Optimiza bases de datos"""
    from src.ncd.neo4j_manager import Neo4jManager
    
    neo4j_config = {
        'uri': 'bolt://localhost:7687',
        'user': 'neo4j',
        'password': os.getenv('NEO4J_PASSWORD')
    }
    
    try:
        manager = Neo4jManager(**neo4j_config)
        manager.execute_query("CALL db.indexes()")
        manager.execute_query("CALL db.awaitIndexes()")
    except Exception as e:
        logging.error(f"Error optimizing databases: {str(e)}")

def rotate_logs():
    """Rota los logs de aplicación"""
    import logging
    from logging.handlers import RotatingFileHandler
    
    # Forzar rotación de todos los handlers de archivo
    for handler in logging.getLogger('acag').handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()
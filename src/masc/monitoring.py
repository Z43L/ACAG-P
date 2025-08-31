from typing import Dict, Any
import json
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class MonitoringMetrics:
    """Métricas de monitorización del MASC"""
    learning_cycles_completed: int = 0
    training_samples_processed: int = 0
    models_deployed: int = 0
    average_improvement: float = 0.0
    last_successful_cycle: datetime = None
    total_training_time_seconds: int = 0

class MASCMonitor:
    """Sistema de monitorización y métricas del MASC"""
    
    def __init__(self, metrics_file: str = "/var/log/acag/masc_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics = MonitoringMetrics()
        self.logger = logging.getLogger(__name__)
        self._load_metrics()
        
    def _load_metrics(self) -> None:
        """Carga métricas desde archivo"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    self.metrics = MonitoringMetrics(**data)
        except Exception as e:
            self.logger.warning(f"Error cargando métricas: {str(e)}")
            
    def _save_metrics(self) -> None:
        """Guarda métricas en archivo"""
        try:
            os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics.__dict__, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error guardando métricas: {str(e)}")
            
    def record_learning_cycle(self, success: bool, samples_processed: int,
                           improvement: float, training_time: int) -> None:
        """Registra un ciclo de aprendizaje"""
        self.metrics.learning_cycles_completed += 1
        
        if success:
            self.metrics.training_samples_processed += samples_processed
            self.metrics.models_deployed += 1
            self.metrics.average_improvement = (
                (self.metrics.average_improvement * (self.metrics.models_deployed - 1) + improvement)
                / self.metrics.models_deployed
            )
            self.metrics.last_successful_cycle = datetime.now()
            self.metrics.total_training_time_seconds += training_time
            
        self._save_metrics()
        
    def get_metrics_report(self) -> Dict[str, Any]:
        """Genera un reporte de métricas"""
        return {
            'learning_cycles_completed': self.metrics.learning_cycles_completed,
            'training_samples_processed': self.metrics.training_samples_processed,
            'models_deployed': self.metrics.models_deployed,
            'average_improvement': round(self.metrics.average_improvement, 3),
            'last_successful_cycle': self.metrics.last_successful_cycle.isoformat() if self.metrics.last_successful_cycle else None,
            'total_training_hours': round(self.metrics.total_training_time_seconds / 3600, 1),
            'avg_samples_per_cycle': round(self.metrics.training_samples_processed / max(1, self.metrics.models_deployed), 0)
        }
        
    def check_system_health(self) -> Dict[str, bool]:
        """Verifica la salud del sistema MASC"""
        return {
            'storage_available': self._check_storage(),
            'gpu_available': torch.cuda.is_available(),
            'ncd_accessible': self._check_ncd_connection(),
            'art_accessible': self._check_art_connection(),
            'recent_activity': self._check_recent_activity()
        }
        
    def _check_storage(self) -> bool:
        """Verifica disponibilidad de almacenamiento"""
        try:
            return os.path.exists('./models') and os.access('./models', os.W_OK)
        except:
            return False
            
    def _check_ncd_connection(self) -> bool:
        """Verifica conexión con NCD"""
        # Implementación específica
        return True
        
    def _check_art_connection(self) -> bool:
        """Verifica conexión con ART"""
        # Implementación específica
        return True
        
    def _check_recent_activity(self) -> bool:
        """Verifica actividad reciente"""
        if not self.metrics.last_successful_cycle:
            return False
            
        time_since_last = datetime.now() - self.metrics.last_successful_cycle
        return time_since_last.days < 7  # Activo si hubo actividad en la última semana
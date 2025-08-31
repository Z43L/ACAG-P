from typing import Dict, Any
import logging
from datetime import datetime

def setup_learning_monitoring(config: Dict[str, Any]) -> logging.Logger:
    """Configura el sistema de logging para el aprendizaje continuo"""
    logger = logging.getLogger("acag_masc")
    logger.setLevel(config.get("log_level", "INFO"))
    
    # Handler para archivo
    file_handler = logging.FileHandler(
        config.get("log_file", "/var/log/acag/masc.log")
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class PerformanceMonitor:
    """Monitoriza el rendimiento del sistema de aprendizaje"""
    
    def __init__(self):
        self.metrics = {
            "training_time": [],
            "memory_usage": [],
            "gpu_utilization": [],
            "throughput": []
        }
    
    def record_metric(self, metric_name: str, value: float):
        """Registra una métrica de performance"""
        if metric_name in self.metrics:
            self.metrics[metric_name].append({
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Genera un reporte de performance"""
        report = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                report[f"{metric_name}_avg"] = sum(v["value"] for v in values) / len(values)
                report[f"{metric_name}_max"] = max(v["value"] for v in values)
                report[f"{metric_name}_min"] = min(v["value"] for v in values)
        
        return report
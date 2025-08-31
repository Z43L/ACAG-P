from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
from typing import Dict, Any
import psutil
import logging

class MetricsExporter:
    """Exporta métricas críticas del sistema ACAG-P para Prometheus"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.logger = logging.getLogger(__name__)
        
        # Métricas de rendimiento
        self.cpu_usage = Gauge('acag_cpu_usage_percent', 'CPU usage percentage')
        self.memory_usage = Gauge('acag_memory_usage_bytes', 'Memory usage in bytes')
        self.disk_usage = Gauge('acag_disk_usage_percent', 'Disk usage percentage')
        
        # Métricas de aplicación
        self.request_count = Counter('acag_requests_total', 'Total requests served')
        self.request_duration = Histogram('acag_request_duration_seconds', 'Request duration in seconds')
        self.error_count = Counter('acag_errors_total', 'Total errors encountered')
        
        # Métricas de modelos
        self.model_inference_time = Histogram('acag_model_inference_seconds', 'Model inference time')
        self.model_cache_size = Gauge('acag_model_cache_size', 'Number of cached models')
        
    def start_exporting(self):
        """Inicia el servidor de exportación de métricas"""
        start_http_server(self.port)
        self.logger.info(f"Metrics exporter started on port {self.port}")
        
    def update_system_metrics(self):
        """Actualiza las métricas del sistema"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        self.disk_usage.set(disk.percent)
        
    def record_request(self, duration: float, success: bool = True):
        """Registra una solicitud procesada"""
        self.request_count.inc()
        self.request_duration.observe(duration)
        
        if not success:
            self.error_count.inc()
            
    def record_model_inference(self, model_name: str, duration: float):
        """Registra una inferencia de modelo"""
        self.model_inference_time.observe(duration)
        
    def update_model_cache_metrics(self, cache_size: int):
        """Actualiza métricas de caché de modelos"""
        self.model_cache_size.set(cache_size)
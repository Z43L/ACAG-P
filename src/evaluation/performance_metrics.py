from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np
from prometheus_client import Gauge, Counter, Histogram

@dataclass
class PerformanceMetrics:
    """Métricas técnicas de rendimiento del sistema ACAG-P"""
    
    # Tiempos de respuesta
    mean_response_time: float
    p95_response_time: float
    p99_response_time: float
    
    # Throughput
    requests_per_second: float
    successful_requests: int
    failed_requests: int
    
    # Uso de recursos
    cpu_usage_percent: float
    memory_usage_mb: float
    gpu_usage_percent: Optional[float]
    
    # Eficiencia de modelos
    local_model_usage_ratio: float
    external_model_usage_ratio: float
    cache_hit_rate: float
    
    @classmethod
    def create_prometheus_metrics(cls, registry):
        """Crea métricas Prometheus para seguimiento continuo"""
        return {
            'response_time': Histogram(
                'acag_response_time_seconds',
                'Tiempo de respuesta del sistema',
                ['endpoint'],
                registry=registry
            ),
            'requests_total': Counter(
                'acag_requests_total',
                'Total de requests procesados',
                ['endpoint', 'status'],
                registry=registry
            ),
            'resource_usage': Gauge(
                'acag_resource_usage',
                'Uso de recursos del sistema',
                ['resource_type'],
                registry=registry
            )
        }
    
    def record_metrics(self, prometheus_metrics: Dict):
        """Registra las métricas en Prometheus"""
        # Registrar tiempos de respuesta
        for endpoint, times in self.response_times.items():
            for time in times:
                prometheus_metrics['response_time'].labels(endpoint=endpoint).observe(time)
        
        # Registrar uso de recursos
        prometheus_metrics['resource_usage'].labels(resource_type='cpu').set(self.cpu_usage_percent)
        prometheus_metrics['resource_usage'].labels(resource_type='memory').set(self.memory_usage_mb)
        
        if self.gpu_usage_percent is not None:
            prometheus_metrics['resource_usage'].labels(resource_type='gpu').set(self.gpu_usage_percent)

class PerformanceEvaluator:
    """Evalúa el rendimiento técnico del sistema ACAG-P"""
    
    def __init__(self):
        self.metrics_history = []
        
    def evaluate_performance(self, log_data: List[Dict]) -> PerformanceMetrics:
        """Evalúa el rendimiento a partir de datos de log"""
        response_times = self._extract_response_times(log_data)
        success_rates = self._calculate_success_rates(log_data)
        resource_usage = self._analyze_resource_usage(log_data)
        
        metrics = PerformanceMetrics(
            mean_response_time=np.mean(response_times) if response_times else 0,
            p95_response_time=np.percentile(response_times, 95) if response_times else 0,
            p99_response_time=np.percentile(response_times, 99) if response_times else 0,
            requests_per_second=self._calculate_throughput(log_data),
            successful_requests=success_rates['successful'],
            failed_requests=success_rates['failed'],
            cpu_usage_percent=resource_usage.get('cpu', 0),
            memory_usage_mb=resource_usage.get('memory', 0),
            gpu_usage_percent=resource_usage.get('gpu'),
            local_model_usage_ratio=self._calculate_model_usage_ratio(log_data),
            external_model_usage_ratio=1 - self._calculate_model_usage_ratio(log_data),
            cache_hit_rate=self._calculate_cache_hit_rate(log_data)
        )
        
        self.metrics_history.append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })
        
        return metrics
    
    def _extract_response_times(self, log_data: List[Dict]) -> List[float]:
        """Extrae tiempos de respuesta de los logs"""
        return [log['response_time'] for log in log_data if 'response_time' in log]
    
    def _calculate_success_rates(self, log_data: List[Dict]) -> Dict[str, int]:
        """Calcula tasas de éxito y error"""
        successful = sum(1 for log in log_data if log.get('status') == 'success')
        failed = sum(1 for log in log_data if log.get('status') == 'error')
        
        return {'successful': successful, 'failed': failed}
    
    def _calculate_throughput(self, log_data: List[Dict]) -> float:
        """Calcula el throughput del sistema"""
        if not log_data:
            return 0.0
        
        timestamps = [log['timestamp'] for log in log_data]
        time_range = max(timestamps) - min(timestamps)
        
        if time_range.total_seconds() == 0:
            return len(log_data)
        
        return len(log_data) / time_range.total_seconds()
    
    def _analyze_resource_usage(self, log_data: List[Dict]) -> Dict[str, float]:
        """Analiza el uso de recursos desde los logs"""
        # Implementación simplificada
        cpu_readings = [log.get('cpu_usage', 0) for log in log_data if 'cpu_usage' in log]
        memory_readings = [log.get('memory_usage', 0) for log in log_data if 'memory_usage' in log]
        gpu_readings = [log.get('gpu_usage', 0) for log in log_data if 'gpu_usage' in log]
        
        return {
            'cpu': np.mean(cpu_readings) if cpu_readings else 0,
            'memory': np.mean(memory_readings) if memory_readings else 0,
            'gpu': np.mean(gpu_readings) if gpu_readings else None
        }
from typing import Dict, List, Any
from datetime import datetime, timedelta
import time
import psutil
import logging

class PerformanceMonitor:
    """Monitoriza el rendimiento y salud del MIU"""
    
    def __init__(self):
        self.metrics = {
            'processing_times': [],
            'throughput': [],
            'error_rates': [],
            'resource_usage': []
        }
        self.start_time = datetime.now()
        self.logger = logging.getLogger('miu.performance')
        
    def record_processing_time(self, adapter_type: str, processingtime: float) -> None:
        """Registra el tiempo de procesamiento de un adaptador"""
        self.metrics['processing_times'].append({
            'timestamp': datetime.now().isoformat(),
            'adapter_type': adapter_type,
            'processing_time': processing_time
        })
        
    def record_throughput(self, items_processed: int, interval: float = 1.0) -> None:
        """Registra el throughput del sistema"""
        throughput = items_processed / interval
        self.metrics['throughput'].append({
            'timestamp': datetime.now().isoformat(),
            'throughput': throughput,
            'items_processed': items_processed
        })
        
    def record_error(self, adapter_type: str, error_type: str) -> None:
        """Registra un error ocurrido"""
        self.metrics['error_rates'].append({
            'timestamp': datetime.now().isoformat(),
            'adapter_type': adapter_type,
            'error_type': error_type
        })
        
    def record_resource_usage(self) -> None:
        """Registra el uso actual de recursos del sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_usage = psutil.disk_usage('/')
        
        self.metrics['resource_usage'].append({
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory_info.percent,
           'memory_used_gb': memory_info.used / (1024**3),
            'disk_percent': disk_usage.percent,
            'disk_free_gb': disk_usage.free / (1024**3)
        })
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Genera un reporte completo de rendimiento"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Calcular métricas agregadas
        avg_processing_time = self._calculate_avg_processing_time()
        avg_throughput = self._calculate_avg_throughput()
        error_rate = self._calculate_error_rate()
        current_resources = self._get_current_resources()
        
        return {
            'timestamp': now.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'average_processing_time': avg_processing_time,
            'average_throughput': avg_throughput,
            'error_rate': error_rate,
            'resource_usage': current_resources,
            'total_items_processed': len(self.metrics['processing_times']),
            'total_errors': len(self.metrics['error_rates'])
        }
        
    def _calculate_avg_processing_time(self) -> Dict[str, float]:
        """Calcula el tiempo promedio de procesamiento por adaptador"""
        times_by_adapter = {}
        counts_by_adapter = {}
        
        for record in self.metrics['processing_times']:
            adapter = record['adapter_type']
            time_val = record['processing_time']
            
            if adapter not in times_by_adapter:
                times_by_adapter[adapter] = 0.0
                counts_by_adapter[adapter] = 0
                
            times_by_adapter[adapter] += time_val
            counts_by_adapter[adapter] += 1
            
        averages = {}
        for adapter, total_time in times_by_adapter.items():
            averages[adapter] = total_time / counts_by_adapter[adapter]
            
        return averages
        
    def _calculate_avg_throughput(self) -> float:
        """Calcula the throughput promedio"""
        if not self.metrics['throughput']:
            return 0.0
            
        total_throughput = sum(record['throughput'] for record in self.metrics['throughput'])
        return total_throughput / len(self.metrics['throughput'])
        
    def _calculate_error_rate(self) -> float:
        """Calcula la tasa de error"""
        total_operations = len(self.metrics['processing_times'])
        total_errors = len(self.metrics['error_rates'])
        
        if total_operations == 0:
            return 0.0
            
        return total_errors / total_operations
        
    def _get_current_resources(self) -> Dict[str, Any]:
        """Obtiene el uso actual de recursos"""
        if not self.metrics['resource_usage']:
            return {}
            
        return self.metrics['resource_usage'][-1]
        
    def start_monitoring_loop(self, interval: int = 60) -> None:
        """Inicia el monitoreo continuo de recursos"""
        import threading
        
        def monitor_loop():
            while true:
                self.record_resource_usage()
                time.sleep(interval)
                
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        self.logger.info(f"Started resource monitoring with {interval}s interval")
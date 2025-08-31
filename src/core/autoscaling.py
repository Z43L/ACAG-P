from typing import Dict, Any
from datetime import datetime, timedelta
import statistics

class AutoScaler:
    """Sistema de auto-escalado para ACAG-P basado en métricas de carga"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history = []
        self.scaling_actions = []
        
    def analyze_metrics(self, current_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Analiza las métricas actuales y decide acciones de escalado"""
        self.metrics_history.append({
            'timestamp': datetime.now().isoformat(),
            'metrics': current_metrics
        })
        
        # Mantener solo historial reciente
        self._prune_history()
        
        analysis = {
            'cpu_analysis': self._analyze_cpu(current_metrics['cpu_usage']),
            'memory_analysis': self._analyze_memory(current_metrics['memory_usage']),
            'throughput_analysis': self._analyze_throughput(current_metrics['requests_per_second']),
            'recommended_action': None
        }
        
        # Decidir acción basada en el análisis
        analysis['recommended_action'] = self._decide_scaling_action(analysis)
        
        if analysis['recommended_action']:
            self._execute_scaling_action(analysis['recommended_action'])
            
        return analysis
        
    def _analyze_cpu(self, current_cpu: float) -> Dict[str, Any]:
        """Analiza el uso de CPU"""
        cpu_history = [m['metrics']['cpu_usage'] for m in self.metrics_history]
        avg_cpu = statistics.mean(cpu_history) if cpu_history else 0
        
        return {
            'current': current_cpu,
            'average': avg_cpu,
            'trend': self._calculate_trend(cpu_history),
            'status': 'high' if current_cpu > 80 else 'normal'
        }
        
    def _analyze_memory(self, current_memory: float) -> Dict[str, Any]:
        """Analiza el uso de memoria"""
        memory_history = [m['metrics']['memory_usage'] for m in self.metrics_history]
        avg_memory = statistics.mean(memory_history) if memory_history else 0
        
        return {
            'current': current_memory,
            'average': avg_memory,
            'trend': self._calculate_trend(memory_history),
            'status': 'high' if current_memory > 85 else 'normal'
        }
        
    def _analyze_throughput(self, current_throughput: float) -> Dict[str, Any]:
        """Analiza el throughput de requests"""
        throughput_history = [m['metrics']['requests_per_second'] for m in self.metrics_history]
        avg_throughput = statistics.mean(throughput_history) if throughput_history else 0
        
        return {
            'current': current_throughput,
            'average': avg_throughput,
            'trend': self._calculate_trend(throughput_history),
            'status': 'high' if current_throughput > self.config.get('throughput_threshold', 100) else 'normal'
        }
        
    def _decide_scaling_action(self, analysis: Dict[str, Any]) -> str:
        """Decide la acción de escalado basada en el análisis"""
        # Lógica compleja de decisión basada en múltiples factores
        if (analysis['cpu_analysis']['status'] == 'high' and 
            analysis['memory_analysis']['status'] == 'high'):
            return 'scale_out'
            
        elif (analysis['throughput_analysis']['status'] == 'high' and 
              analysis['cpu_analysis']['trend'] == 'increasing'):
            return 'scale_out'
            
        elif (analysis['cpu_analysis']['status'] == 'normal' and 
              analysis['memory_analysis']['status'] == 'normal' and
              analysis['throughput_analysis']['current'] < 50):
            return 'scale_in'
            
        return None
        
    def _execute_scaling_action(self, action: str) -> None:
        """Ejecuta la acción de escalado"""
        scaling_action = {
            'action': action,
            'timestamp': datetime.now().isoformat(),
            'details': self._get_action_details(action)
        }
        
        self.scaling_actions.append(scaling_action)
        
        # Implementar la acción real (ej: llamar a Kubernetes API, Docker API, etc.)
        self._implement_scaling(action)
from typing import Dict, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class LearningMonitor:
    """Monitoriza y visualiza el progreso del aprendizaje continuo"""
    
    def __init__(self, log_file: str = "data/learning_log.jsonl"):
        self.log_file = log_file
        self.learning_history = self._load_history()
    
    def log_training_session(self, session_data: Dict[str, Any]) -> None:
        """Registra una sesión de entrenamiento"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            **session_data
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        self.learning_history.append(log_entry)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de performance del aprendizaje"""
        if not self.learning_history:
            return {}
        
        successful_sessions = [
            s for s in self.learning_history 
            if s.get("status") == "success"
        ]
        
        success_rate = len(successful_sessions) / len(self.learning_history)
        
        # Calcular mejora promedio
        improvements = [
            s.get("evaluation_result", {}).get("total_improvement", 0)
            for s in successful_sessions
        ]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        return {
            "total_sessions": len(self.learning_history),
            "successful_sessions": len(successful_sessions),
            "success_rate": success_rate,
            "average_improvement": avg_improvement,
            "last_successful_session": successful_sessions[-1]["timestamp"] if successful_sessions else None
        }
    
    def plot_learning_progress(self) -> None:
        """Genera visualizaciones del progreso de aprendizaje"""
        if not self.learning_history:
            return
        
        # Preparar datos para visualización
        dates = []
        improvements = []
        
        for session in self.learning_history:
            if session.get("status") == "success":
                dates.append(datetime.fromisoformat(session["timestamp"]))
                improvements.append(session.get("evaluation_result", {}).get("total_improvement", 0))
        
        if not dates:
            return
        
        # Crear gráfico
        plt.figure(figsize=(10, 6))
        plt.plot(dates, improvements, 'b-', marker='o')
        plt.title("Progreso de Aprendizaje Continuo")
        plt.xlabel("Fecha")
        plt.ylabel("Mejora en Evaluación")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        plt.savefig("reports/learning_progress.png")
        plt.close()
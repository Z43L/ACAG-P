from typing import Dict, Any
from datetime import datetime, timedelta
import json
import os

class CostTracker:
    """Sistema de seguimiento y gestión de costos de API"""
    
    def __init__(self, cost_file: str = "data/costs.json"):
        self.cost_file = cost_file
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
        self.api_calls: Dict[str, int] = {}
        self._load_costs()
        
    def _load_costs(self) -> None:
        """Carga costos históricos desde archivo"""
        if os.path.exists(self.cost_file):
            try:
                with open(self.cost_file, 'r') as f:
                    data = json.load(f)
                    self.daily_cost = data.get('daily_cost', 0.0)
                    self.monthly_cost = data.get('monthly_cost', 0.0)
                    self.api_calls = data.get('api_calls', {})
            except:
                # Si hay error, inicializar valores por defecto
                self._initialize_costs()
        else:
            self._initialize_costs()
            
    def _initialize_costs(self) -> None:
        """Inicializa valores de costo por defecto"""
        self.daily_cost = 0.0
        self.monthly_cost = 0.0
        self.api_calls = {}
        
    def record_api_call(self, model: str, input_tokens: int, output_tokens: int) -> None:
        """Registra una llamada a API y calcula su costo"""
        cost_rates = {
            'claude-2': {'input': 0.000011, 'output': 0.000032},
            'gpt-4': {'input': 0.00003, 'output': 0.00006},
            'llama-2-70b': {'input': 0.0000009, 'output': 0.0000009}
        }
        
        rate = cost_rates.get(model, cost_rates['claude-2'])
        cost = (input_tokens * rate['input']) + (output_tokens * rate['output'])
        
        self.daily_cost += cost
        self.monthly_cost += cost
        
        # Actualizar contador de llamadas
        if model not in self.api_calls:
            self.api_calls[model] = 0
        self.api_calls[model] += 1
        
        self._save_costs()
        
    def _save_costs(self) -> None:
        """Guarda costos actualizados en archivo"""
        data = {
            'daily_cost': self.daily_cost,
            'monthly_cost': self.monthly_cost,
            'api_calls': self.api_calls,
            'last_updated': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.cost_file), exist_ok=True)
        with open(self.cost_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def reset_daily_costs(self) -> None:
        """Reinicia el contador diario de costos"""
        self.daily_cost = 0.0
        self._save_costs()
        
    def get_cost_report(self) -> Dict[str, Any]:
        """Genera un reporte de costos"""
        return {
            'daily_cost': self.daily_cost,
            'monthly_cost': self.monthly_cost,
            'api_calls': self.api_calls,
            'estimated_monthly': self.monthly_cost * 30
        }
from typing import Dict, Any, Optional
import yaml
import json
from pathlib import Path
from functools import lru_cache

class ConfigLoader:
    """Carga y gestiona configuraciones por entorno"""
    
    def __init__(self, env: str = "development"):
        self.env = env
        self.config_dir = Path("config")
        self.base_config = self._load_config_file("base.yaml")
        self.env_config = self._load_config_file(f"{env}.yaml")
        
    def _load_config_file(self, filename: str) -> Dict[str, Any]:
        """Carga un archivo de configuración YAML"""
        file_path = self.config_dir / filename
        
        if not file_path.exists():
            return {}
            
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}
            
    @lru_cache(maxsize=1)
    def get_config(self) -> Dict[str, Any]:
        """Obtiene la configuración combinada para el entorno actual"""
        config = self.base_config.copy()
        
        # Mergear configuración específica del entorno
        for key, value in self.env_config.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key].update(value)
            else:
                config[key] = value
                
        return config
        
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Obtiene configuración específica para un módulo"""
        config = self.get_config()
        return config.get("modules", {}).get(module_name, {})
        
    def save_config(self, config: Dict[str, Any], env: Optional[str] = None) -> None:
        """Guarda configuración para un entorno específico"""
        env = env or self.env
        file_path = self.config_dir / f"{env}.yaml"
        
        with open(file_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
    def validate_config(self) -> bool:
        """Valida que la configuración sea correcta"""
        config = self.get_config()
        required_keys = ["database", "api", "logging"]
        
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Configuración requerida faltante: {key}")
                
        return True

# Instancia global del cargador de configuración
config_loader = ConfigLoader()
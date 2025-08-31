from typing import Dict, List, Any
from datetime import datetime
import hashlib
import json
from pathlib import Path

class ModelVersionManager:
    """Gestiona el versionado y actualización de modelos en ACAG-P"""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.versions_file = self.models_dir / "versions.json"
        self.versions = self._load_versions()
        
    def _load_versions(self) -> List[Dict[str, Any]]:
        """Carga el historial de versiones desde el archivo"""
        if self.versions_file.exists():
            with open(self.versions_file, 'r') as f:
                return json.load(f)
        return []
        
    def register_new_version(self, model_path: str, metadata: Dict[str, Any]) -> str:
        """Registra una nueva versión del modelo"""
        version_id = self._generate_version_id(model_path)
        
        version_data = {
            'version_id': version_id,
            'model_path': str(model_path),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata,
            'checksum': self._calculate_checksum(model_path)
        }
        
        self.versions.append(version_data)
        self._save_versions()
        
        return version_id
        
    def get_latest_version(self) -> Dict[str, Any]:
        """Obtiene la versión más reciente"""
        if not self.versions:
            return None
            
        # Ordenar por timestamp descendente
        sorted_versions = sorted(self.versions, 
                              key=lambda x: x['timestamp'], 
                              reverse=True)
        return sorted_versions[0]
        
    def rollback_version(self, version_id: str) -> bool:
        """Revierte a una versión específica"""
        target_version = next((v for v in self.versions if v['version_id'] == version_id), None)
        
        if not target_version:
            return False
            
        # Implementar lógica de rollback específica
        # Esto podría involucrar copiar archivos, actualizar configuraciones, etc.
        return self._execute_rollback(target_version)
        
    def _generate_version_id(self, model_path: str) -> str:
        """Genera un ID único para la versión"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"model_{timestamp}_{hashlib.md5(model_path.encode()).hexdigest()[:8]}"
        
    def _calculate_checksum(self, model_path: str) -> str:
        """Calcula checksum para verificar integridad"""
        model_files = list(Path(model_path).glob("**/*"))
        all_content = b""
        
        for file in model_files:
            if file.is_file():
                with open(file, 'rb') as f:
                    all_content += f.read()
                    
        return hashlib.md5(all_content).hexdigest()
        
    def validate_version(self, version_id: str) -> bool:
        """Valida la integridad de una versión"""
        version = next((v for v in self.versions if v['version_id'] == version_id), None)
        
        if not version:
            return False
            
        current_checksum = self._calculate_checksum(version['model_path'])
        return current_checksum == version['checksum']
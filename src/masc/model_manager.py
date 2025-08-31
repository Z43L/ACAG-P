import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any

class ModelVersionManager:
    """Gestiona el versionado y checkpoints de modelos en ACAG-P"""
    
    def __init__(self, models_dir: str = "models/versions"):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        self.version_history = self._load_version_history()
    
    def create_checkpoint(self, model_path: str, metadata: Dict[str, Any]) -> str:
        """Crea un checkpoint del modelo actual"""
        checkpoint_id = f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        checkpoint_path = os.path.join(self.models_dir, checkpoint_id)
        
        # Copiar modelo
        shutil.copytree(model_path, checkpoint_path)
        
        # Guardar metadata
        metadata_file = os.path.join(checkpoint_path, "metadata.json")
        with open(metadata_file, "w") as f:
            json.dump({
                **metadata,
                "created_at": datetime.now().isoformat(),
                "checkpoint_id": checkpoint_id
            }, f, indent=2)
        
        # Actualizar historial
        self.version_history.append({
            "checkpoint_id": checkpoint_id,
            "path": checkpoint_path,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata
        })
        
        self._save_version_history()
        return checkpoint_id
    
    def get_latest_checkpoint(self) -> Dict[str, Any]:
        """Obtiene el checkpoint más reciente"""
        if not self.version_history:
            return None
        
        return self.version_history[-1]
    
    def restore_checkpoint(self, checkpoint_id: str) -> str:
        """Restaura un checkpoint específico"""
        checkpoint = next(
            (c for c in self.version_history if c["checkpoint_id"] == checkpoint_id),
            None
        )
        
        if not checkpoint:
            raise ValueError(f"Checkpoint {checkpoint_id} no encontrado")
        
        return checkpoint["path"]
    
    def cleanup_old_checkpoints(self, max_checkpoints: int = 10):
        """Limpia checkpoints antiguos manteniendo solo los más recientes"""
        if len(self.version_history) <= max_checkpoints:
            return
        
        # Ordenar por fecha (más antiguos primero)
        sorted_checkpoints = sorted(
            self.version_history,
            key=lambda x: x["created_at"]
        )
        
        # Eliminar los más antiguos
        for checkpoint in sorted_checkpoints[:-max_checkpoints]:
            try:
                shutil.rmtree(checkpoint["path"])
                self.version_history.remove(checkpoint)
            except Exception as e:
                print(f"Error eliminando checkpoint {checkpoint['checkpoint_id']}: {str(e)}")
        
        self._save_version_history()
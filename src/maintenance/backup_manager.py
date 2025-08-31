from typing import Dict, List, Any
from datetime import datetime
import shutil
import tarfile
import os
import json
from pathlib import Path

class BackupManager:
    """Gestiona los backups del sistema ACAG-P"""
    
    def __init__(self, backup_dir: str, retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """Crea un backup del sistema"""
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{backup_type}"
        backup_path = self.backup_dir / backup_id
        
        try:
            backup_path.mkdir()
            
            # Backup de bases de datos
            self._backup_databases(backup_path)
            
            # Backup de modelos
            self._backup_models(backup_path)
            
            # Backup de configuración
            self._backup_configuration(backup_path)
            
            # Backup de datos de aplicación
            self._backup_application_data(backup_path)
            
            # Crear archivo comprimido
            archive_path = self._create_archive(backup_path)
            
            # Limpiar directorio temporal
            shutil.rmtree(backup_path)
            
            # Registrar backup
            backup_info = {
                'id': backup_id,
                'type': backup_type,
                'path': str(archive_path),
                'size': archive_path.stat().st_size,
                'created_at': datetime.now().isoformat(),
                'checksum': self._calculate_checksum(archive_path)
            }
            
            self._register_backup(backup_info)
            self._cleanup_old_backups()
            
            return backup_info
            
        except Exception as e:
            # Limpiar en caso de error
            if backup_path.exists():
                shutil.rmtree(backup_path)
            raise e
            
    def restore_backup(self, backup_id: str) -> Dict[str, Any]:
        """Restaura el sistema desde un backup"""
        backup_info = self._get_backup_info(backup_id)
        
        if not backup_info:
            raise ValueError(f"Backup {backup_id} not found")
            
        try:
            # Extraer archivo de backup
            extract_path = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._extract_archive(Path(backup_info['path']), extract_path)
            
            # Restaurar componentes
            self._restore_databases(extract_path)
            self._restore_models(extract_path)
            self._restore_configuration(extract_path)
            self._restore_application_data(extract_path)
            
            # Limpiar
            shutil.rmtree(extract_path)
            
            return {
                'status': 'success',
                'backup_id': backup_id,
                'restored_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            if extract_path.exists():
                shutil.rmtree(extract_path)
            raise e
            
    def _cleanup_old_backups(self):
        """Elimina backups antiguos según la política de retención"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                
    def _register_backup(self, backup_info: Dict[str, Any]):
        """Registra el backup en el índice"""
        index_file = self.backup_dir / "backups.json"
        
        if index_file.exists():
            with open(index_file, 'r') as f:
                backups = json.load(f)
        else:
            backups = []
            
        backups.append(backup_info)
        
        with open(index_file, 'w') as f:
            json.dump(backups, f, indent=2)
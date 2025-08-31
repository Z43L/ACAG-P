from typing import Dict, Any, Optional
import shutil
import json
from datetime import datetime
import logging
import hashlib

class DeploymentManager:
    """Gestiona el despliegue seguro de nuevos modelos"""
    
    def __init__(self, art_client, backup_dir: str = "./models/backups"):
        self.art_client = art_client
        self.backup_dir = backup_dir
        self.logger = logging.getLogger(__name__)
        self.deployment_history: List[Dict[str, Any]] = []
        
    def deploy_model(self, model_path: str, validation_report: Dict[str, Any]) -> bool:
        """Despliega un nuevo modelo de manera segura"""
        try:
            # 1. Crear backup del modelo actual
            current_model_path = self.art_client.get_model_path()
            if current_model_path:
                self._create_backup(current_model_path)
                
            # 2. Verificar integridad del nuevo modelo
            if not self._verify_model_integrity(model_path):
                raise ValueError("Integridad del modelo no verificada")
                
            # 3. Actualizar referencia en ART
            success = self.art_client.update_model(model_path)
            
            if success:
                # 4. Registrar despliegue
                self._record_deployment(model_path, validation_report)
                self.logger.info(f"Modelo desplegado exitosamente: {model_path}")
                return True
            else:
                # 5. Restaurar backup si falla
                self._restore_backup()
                return False
                
        except Exception as e:
            self.logger.error(f"Error en despliegue: {str(e)}")
            self._restore_backup()
            return False
            
    def _create_backup(self, model_path: str) -> str:
        """Crea un backup del modelo actual"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{self.backup_dir}/backup_{timestamp}"
        
        shutil.copytree(model_path, backup_path)
        self.logger.info(f"Backup creado: {backup_path}")
        return backup_path
        
    def _verify_model_integrity(self, model_path: str) -> bool:
        """Verifica la integridad del modelo"""
        required_files = ['pytorch_model.bin', 'config.json', 'tokenizer.json']
        
        for file in required_files:
            if not os.path.exists(f"{model_path}/{file}"):
                self.logger.error(f"Archivo requerido faltante: {file}")
                return False
                
        # Verificar checksum de archivos principales
        try:
            with open(f"{model_path}/pytorch_model.bin", 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            # Aquí se podría verificar contra un checksum conocido
            return True
        except Exception as e:
            self.logger.error(f"Error verificando checksum: {str(e)}")
            return False
            
    def _record_deployment(self, model_path: str, validation_report: Dict[str, Any]) -> None:
        """Registra el despliegue en el historial"""
        deployment_record = {
            'timestamp': datetime.now().isoformat(),
            'model_path': model_path,
            'validation_report': validation_report,
            'model_size': self._get_model_size(model_path),
            'performance_metrics': validation_report.get('new_scores', {})
        }
        
        self.deployment_history.append(deployment_record)
        
        # Guardar historial en archivo
        with open(f"{self.backup_dir}/deployment_history.json", 'w') as f:
            json.dump(self.deployment_history, f, indent=2)
            
    def _get_model_size(self, model_path: str) -> int:
        """Calcula el tamaño del modelo en MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(model_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size // (1024 * 1024)  # Convertir a MB
        
    def _restore_backup(self) -> bool:
        """Restaura el último backup disponible"""
        try:
            # Encontrar el backup más reciente
            backups = [d for d in os.listdir(self.backup_dir) if d.startswith('backup_')]
            if not backups:
                self.logger.error("No hay backups disponibles para restaurar")
                return False
                
            latest_backup = sorted(backups)[-1]
            backup_path = f"{self.backup_dir}/{latest_backup}"
            
            # Restaurar backup
            current_path = self.art_client.get_model_path()
            if current_path:
                shutil.rmtree(current_path)
                shutil.copytree(backup_path, current_path)
                
            self.logger.info(f"Backup restaurado: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restaurando backup: {str(e)}")
            return False
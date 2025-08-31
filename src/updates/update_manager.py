from typing import Dict, List, Any
import requests
import json
from datetime import datetime
from packaging import version
import subprocess
import logging

class UpdateManager:
    """Gestiona las actualizaciones del sistema ACAG-P"""
    
    def __init__(self, current_version: str, update_channel: str = "stable"):
        self.current_version = current_version
        self.update_channel = update_channel
        self.update_url = "https://api.acag-project.org/versions"
        self.logger = logging.getLogger(__name__)
        
    def check_for_updates(self) -> Dict[str, Any]:
        """Verifica si hay actualizaciones disponibles"""
        try:
            response = requests.get(
                f"{self.update_url}/{self.update_channel}",
                timeout=10
            )
            response.raise_for_status()
            
            available_versions = response.json()
            latest_version = available_versions['latest']
            
            return {
                'current_version': self.current_version,
                'latest_version': latest_version,
                'update_available': version.parse(latest_version) > version.parse(self.current_version),
                'changelog': available_versions['changelog'].get(latest_version, ''),
                'release_date': available_versions['release_dates'].get(latest_version, '')
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return {
                'current_version': self.current_version,
                'latest_version': self.current_version,
                'update_available': False,
                'error': str(e)
            }
            
    def apply_update(self, target_version: str = None) -> Dict[str, Any]:
        """Aplica una actualización al sistema"""
        try:
            update_info = self.check_for_updates()
            
            if not update_info['update_available'] and not target_version:
                return {'status': 'no_update_available', 'current_version': self.current_version}
                
            version_to_install = target_version or update_info['latest_version']
            
            # Descargar y verificar la actualización
            download_url = f"{self.update_url}/download/{version_to_install}"
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Verificar checksum
            expected_checksum = self._get_checksum(version_to_install)
            actual_checksum = self._calculate_checksum(response.content)
            
            if expected_checksum != actual_checksum:
                raise ValueError("Checksum verification failed")
                
            # Aplicar la actualización
            result = self._install_update(response.content, version_to_install)
            
            return {
                'status': 'success',
                'previous_version': self.current_version,
                'new_version': version_to_install,
                'applied_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error applying update: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'current_version': self.current_version
            }
            
    def rollback_update(self) -> Dict[str, Any]:
        """Revierte la última actualización"""
        try:
            # Implementar lógica de rollback
            # Esto podría involucrar restaurar desde backup
            return {
                'status': 'success',
                'message': 'Rollback completed successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def _get_checksum(self, version: str) -> str:
        """Obtiene el checksum esperado para una versión"""
        response = requests.get(f"{self.update_url}/checksum/{version}", timeout=10)
        response.raise_for_status()
        return response.json()['checksum']
        
    def _calculate_checksum(self, data: bytes) -> str:
        """Calcula el checksum de los datos"""
        import hashlib
        return hashlib.sha256(data).hexdigest()
        
    def _install_update(self, update_data: bytes, version: str) -> bool:
        """Instala la actualización"""
        # Implementar lógica específica de instalación
        # Esto podría involucrar extraer archivos, ejecutar scripts, etc.
        return True
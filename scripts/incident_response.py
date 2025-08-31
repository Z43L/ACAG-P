#!/usr/bin/env python3
"""
Sistema automatizado de respuesta a incidentes para ACAG-P
"""

import logging
from datetime import datetime
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText

class IncidentResponseSystem:
    """Sistema de gestión y respuesta a incidentes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.incident_history = []
        
    def detect_incident(self, metric_name: str, threshold: float, current_value: float) -> bool:
        """Detecta un incidente basado en métricas"""
        if current_value > threshold:
            incident = {
                'timestamp': datetime.now().isoformat(),
                'metric': metric_name,
                'threshold': threshold,
                'current_value': current_value,
                'severity': self._calculate_severity(metric_name, current_value, threshold)
            }
            self.trigger_response(incident)
            return True
        return False
        
    def trigger_response(self, incident: Dict[str, Any]) -> None:
        """Ejecuta la respuesta automatizada al incidente"""
        self.incident_history.append(incident)
        
        # Notificar al equipo
        self._notify_team(incident)
        
        # Acciones automatizadas basadas en la severidad
        if incident['severity'] == 'critical':
            self._execute_automated_recovery(incident)
            
    def _calculate_severity(self, metric_name: str, value: float, threshold: float) -> str:
        """Calcula la severidad del incidente"""
        ratio = value / threshold
        
        if ratio > 2.0:
            return 'critical'
        elif ratio > 1.5:
            return 'high'
        elif ratio > 1.2:
            return 'medium'
        else:
            return 'low'
            
    def _notify_team(self, incident: Dict[str, Any]) -> None:
        """Notifica al equipo sobre el incidente"""
        subject = f"Incidente {incident['severity'].upper()}: {incident['metric']}"
        body = f"""
        Se ha detectado un incidente en ACAG-P:
        
        Métrica: {incident['metric']}
        Valor actual: {incident['current_value']}
        Umbral: {incident['threshold']}
        Severidad: {incident['severity']}
        Timestamp: {incident['timestamp']}
        
        Acciones recomendadas:
        {self._get_recommended_actions(incident)}
        """
        
        self._send_email(subject, body)
        
    def _execute_automated_recovery(self, incident: Dict[str, Any]) -> None:
        """Ejecuta acciones automatizadas de recuperación"""
        if incident['metric'] == 'memory_usage':
            self._scale_service('worker', 'down', 1)
        elif incident['metric'] == 'response_time':
            self._restart_service('api')
            
    def _get_recommended_actions(self, incident: Dict[str, Any]) -> str:
        """Devuelve acciones recomendadas para el incidente"""
        actions = {
            'memory_usage': 'Considerar escalado horizontal o optimización de memoria',
            'response_time': 'Revisar consultas a BD y optimizar índices',
            'cpu_usage': 'Verificar procesos y considerar escalado',
            'error_rate': 'Revisar logs de aplicación y monitorear excepciones'
        }
        return actions.get(incident['metric'], 'Revisar manualmente')
        
    def generate_incident_report(self, days: int = 30) -> Dict[str, Any]:
        """Genera un reporte de incidentes"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_incidents = [
            i for i in self.incident_history 
            if datetime.fromisoformat(i['timestamp']) > cutoff_date
        ]
        
        return {
            'total_incidents': len(recent_incidents),
            'by_severity': self._group_by_severity(recent_incidents),
            'by_metric': self._group_by_metric(recent_incidents),
            'mean_time_to_resolution': self._calculate_mttr(recent_incidents)
        }
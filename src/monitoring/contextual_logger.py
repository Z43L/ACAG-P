import logging
from typing import Dict, Any
from uuid import uuid4

class ContextualLogger:
    """Logger que mantiene contexto para trazabilidad de solicitudes"""
    
    def __init__(self, base_logger, default_context: Dict[str, Any] = None):
        self.base_logger = base_logger
        self.default_context = default_context or {}
        self.request_id = None
        
    def set_request_context(self, request_id: str = None, context: Dict[str, Any] = None):
        """Establece el contexto para la solicitud actual"""
        self.request_id = request_id or str(uuid4())
        self.default_context.update(context or {})
        self.default_context['request_id'] = self.request_id
        
    def _add_context(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """Añade contexto a los logs"""
        context = self.default_context.copy()
        if extra:
            context.update(extra)
        return context
        
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log nivel info con contexto"""
        self.base_logger.info(message, extra=self._add_context(extra))
        
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log nivel warning con contexto"""
        self.base_logger.warning(message, extra=self._add_context(extra))
        
    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log nivel error con contexto"""
        self.base_logger.error(message, extra=self._add_context(extra))
        
    def critical(self, message: str, extra: Dict[str, Any] = None):
        """Log nivel critical con contexto"""
        self.base_logger.critical(message, extra=self._add_context(extra))
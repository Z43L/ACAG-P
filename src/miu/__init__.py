"""
Módulo de Ingesta Universal (MIU) - ACAG-P
Sistema unificado para ingesta de datos de múltiples fuentes
"""

from typing import Dict, Any
import time
from .adapters.text_adapter import TextAdapter
from .adapters.api_adapter import APIAdapter
from .adapters.database_adapter import DatabaseAdapter
from .adapters.audio_adapter import AudioAdapter
from .quality_validator import DataQualityValidator
from .queue_manager import QueueManager
from .performance_monitor import PerformanceMonitor

class UniversalIngestionModule:
    """Módulo principal de ingesta universal"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.adapters = {}
        self.validator = DataQualityValidator()
        self.queue_manager = QueueManager()
        self.performance_monitor = PerformanceMonitor()
        self.initialized = False
        
    def initialize(self) -> bool:
        """Inicializa el módulo y todos sus componentes"""
        try:
            # Inicializar adaptadores configurados
            self._initialize_adapters()
            
            # Iniciar monitoreo de performance
            self.performance_monitor.start_monitoring_loop()
            
            # Iniciar workers de procesamiento
            self._start_processing_workers()
            
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"Failed to initialize MIU: {str(e)}")
            return False
            
    def _initialize_adapters(self) -> None:
        """Inicializa todos los adaptadores configurados"""
        adapter_configs = self.config.get('adapters', {})
        
        # Adaptador de texto
        if adapter_configs.get('text_enabled', True):
            self.adapters['text'] = TextAdapter(adapter_configs.get('text', {}))
            
        # Adaptador de API
        if adapter_configs.get('api_enabled', True):
            self.adapters['api'] = APIAdapter(adapter_configs.get('api', {}))
            
        # Adaptador de base de datos
        if adapter_configs.get('database_enabled', True):
            self.adapters['database'] = DatabaseAdapter(adapter_configs.get('database', {}))
            
        # Adaptador de audio
        if adapter_configs.get('audio_enabled', False):  # Deshabilitado por defecto
            self.adapters['audio'] = AudioAdapter(adapter_configs.get('audio', {}))
            
    def ingest_data(self, source_type: str, parameters: Dict[str, Any], 
                   priority: str = 'normal') -> str:
        """
        Ingresa datos desde una fuente específica
        
        Args:
            source_type: Tipo de fuente ('text', 'api', 'database', 'audio')
            parameters: Parámetros específicos para el adaptador
            priority: Prioridad de procesamiento
            
        Returns:
            ID o confirmación del ingreso
        """
        if not self.initialized:
            raise Exception("MIU not initialized. Call initialize() first.")
            
        if source_type not in self.adapters:
            raise ValueError(f"Unsupported source type: {source_type}")
            
        try:
            # Extraer datos usando el adaptador apropiado
            adapter = self.adapters[source_type]
            start_time = time.time()
            
            if not adapter.connect():
                raise Exception(f"Failed to connect to {source_type} source")
                
            extracted_data = adapter.extract_data(parameters)
            adapter.close()
            
            # Medir tiempo de procesamiento
            processing_time = time.time() - start_time
            self.performance_monitor.record_processing_time(source_type, processing_time)
            
            # Validar y normalizar datos
            for data_item in extracted_data:
                validation_result = self.validator.validate(dataitem)
                
                if validation_result['is_valid']:
                    normalized_data = self.validator.normalize_data(data_item)
                    
                    # Añadir a la cola de procesamiento
                    self.queue_manager.enqueue(normalized_data, priority)
                    
                    # Registrar throughput
                    self.performance_monitor.record_throughput(1)
                else:
                    self.performance_monitor.record_error(source_type, 'validation_failed')
                    print(f"Validation failed: {validation_result['errors']}")
                    
            return f"Successfully ingested {len(extracted_data)} items from {source_type}"
            
        except Exception as e:
            self.performance_monitor.record_error(source_type, 'ingestion_failed')
            raise Exception(f"Failed to ingest from {source_type}: {str(e)}")
            
    def _start_processing_workers(self) -> None:
        """Inicia workers para procesar datos de las colas"""
        # Este método conectaría con el MPE para procesamiento posterior
        def processing_callback(data: Dict[str, Any]):
            # Aquí se conectaría con el Módulo de Procesamiento y Estructuración
            print(f"Processing data: {data['metadata']['source']}")
            # Simular procesamiento exitoso
            return True
            
        # Iniciar workers para cada prioridad
        self.queue_manager.start_processing_worker(processing_callback, "high_priority_worker")
        self.queue_manager.start_processing_worker(processing_callback, "normal_priority_worker")
        self.queue_manager.start_processing_worker(processing_callback, "low_priority_worker")
        
    def get_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual del módulo"""
        return {
            'initialized': self.initialized,
            'adapters_available': list(self.adapters.keys()),
            'queue_stats': self.queue_manager.get_queue_stats(),
            'performance': self.performance_monitor.get_performance_report()
        }
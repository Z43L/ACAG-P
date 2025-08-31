from typing import Dict, List, Any, Callable
from abc import ABC, abstractmethod
import importlib
import inspect

class ExtensionModule(ABC):
    """Clase base para módulos de extensión de ACAG-P"""
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializa el módulo de extensión"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Devuelve las capacidades que añade este módulo"""
        pass
        
    @abstractmethod
    def execute(self, capability: str, parameters: Dict[str, Any]) -> Any:
        """Ejecuta una capacidad del módulo"""
        pass

class ExtensionManager:
    """Gestiona la carga y ejecución de extensiones"""
    
    def __init__(self):
        self.extensions: Dict[str, ExtensionModule] = {}
        self.capability_map: Dict[str, str] = {}  # capability -> extension_name
        
    def load_extension(self, module_path: str, config: Dict[str, Any]) -> bool:
        """Carga y inicializa una extensión"""
        try:
            module = importlib.import_module(module_path)
            
            # Buscar clases que hereden de ExtensionModule
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, ExtensionModule) and 
                    obj != ExtensionModule):
                    
                    extension = obj()
                    if extension.initialize(config):
                        extension_name = obj.__name__
                        self.extensions[extension_name] = extension
                        
                        # Mapear capacidades
                        for capability in extension.get_capabilities():
                            self.capability_map[capability] = extension_name
                            
                        return True
                        
        except Exception as e:
            print(f"Error loading extension {module_path}: {str(e)}")
            return False
            
    def execute_capability(self, capability: str, parameters: Dict[str, Any]) -> Any:
        """Ejecuta una capacidad de extensión"""
        if capability not in self.capability_map:
            raise ValueError(f"Capability {capability} not available")
            
        extension_name = self.capability_map[capability]
        extension = self.extensions[extension_name]
        
        return extension.execute(capability, parameters)
        
    def get_available_capabilities(self) -> List[str]:
        """Devuelve todas las capacidades disponibles"""
        return list(self.capability_map.keys())
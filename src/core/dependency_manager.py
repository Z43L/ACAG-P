from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ModuleDependencies:
    """Estructura para gestionar dependencias entre módulos"""
    miu: Optional[Any] = None
    mpe: Optional[Any] = None
    ncd: Optional[Any] = None
    art: Optional[Any] = None
    masc: Optional[Any] = None
    mci: Optional[Any] = None

class DependencyManager:
    """Gestiona las dependencias e inyección entre módulos"""
    
    def __init__(self):
        self.modules: Dict[str, Any] = {}
        self.dependencies: Dict[str, ModuleDependencies] = {}
    
    def register_module(self, module_name: str, module_instance: Any) -> None:
        """Registra un módulo en el gestor de dependencias"""
        self.modules[module_name] = module_instance
        self.dependencies[module_name] = ModuleDependencies()
    
    def resolve_dependencies(self) -> None:
        """Resuelve e inyecta todas las dependencias entre módulos"""
        for module_name, module_instance in self.modules.items():
            deps = self.dependencies[module_name]
            
            # Inyectar dependencias basado en el tipo de módulo
            if hasattr(module_instance, 'set_dependencies'):
                module_instance.set_dependencies(
                    **{k: v for k, v in self._get_dependencies_for_module(module_name).items() 
                      if v is not None}
                )
    
    def _get_dependencies_for_module(self, module_name: str) -> Dict[str, Any]:
        """Obtiene las dependencias requeridas para un módulo específico"""
        dependencies = {}
        
        if module_name == 'mpe':
            dependencies['miu'] = self.modules.get('miu')
        elif module_name == 'ncd':
            dependencies['mpe'] = self.modules.get('mpe')
        elif module_name == 'art':
            dependencies['ncd'] = self.modules.get('ncd')
        elif module_name == 'masc':
            dependencies['ncd'] = self.modules.get('ncd')
            dependencies['art'] = self.modules.get('art')
        elif module_name == 'mci':
            dependencies['art'] = self.modules.get('art')
            dependencies['ncd'] = self.modules.get('ncd')
        
        return dependencies
    
    def validate_dependencies(self) -> bool:
        """Valida que todas las dependencias requeridas estén disponibles"""
        for module_name, deps in self.dependencies.items():
            required_deps = self._get_required_dependencies(module_name)
            missing_deps = [
                dep for dep in required_deps 
                if getattr(deps, dep) is None
            ]
            
            if missing_deps:
                raise ValueError(
                    f"Módulo {module_name} requiere dependencias faltantes: {missing_deps}"
                )
        
        return True
    
    def _get_required_dependencies(self, module_name: str) -> list:
        """Obtiene las dependencias requeridas para cada módulo"""
        requirements = {
            'mpe': ['miu'],
            'ncd': ['mpe'],
            'art': ['ncd'],
            'masc': ['ncd', 'art'],
            'mci': ['art', 'ncd']
        }
        return requirements.get(module_name, [])
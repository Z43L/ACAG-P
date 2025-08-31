from typing import Dict, List, Any
from datetime import datetime
import logging
from dataclasses import dataclass

@dataclass
class ImprovementInitiative:
    """Iniciativa de mejora para ACAG-P"""
    id: str
    title: str
    description: str
    priority: str  # high, medium, low
    estimated_effort: int  # días-persona
    expected_impact: str
    status: str  # proposed, approved, in_progress, completed
    created_at: datetime
    completed_at: Optional[datetime]

class ContinuousImprovementManager:
    """Gestiona las iniciativas de mejora continua del sistema"""
    
    def __init__(self):
        self.initiatives = []
        self.logger = logging.getLogger(__name__)
        
    def propose_improvement(self, title: str, description: str, 
                          priority: str, effort: int, impact: str) -> str:
        """Propone una nueva iniciativa de mejora"""
        initiative_id = f"improve_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initiative = ImprovementInitiative(
            id=initiative_id,
            title=title,
            description=description,
            priority=priority,
            estimated_effort=effort,
            expected_impact=impact,
            status="proposed",
            created_at=datetime.now(),
            completed_at=None
        )
        
        self.initiatives.append(initiative)
        self._save_initiatives()
        
        return initiative_id
    
    def review_improvements(self) -> List[ImprovementInitiative]:
        """Revisa las mejoras propuestas para su aprobación"""
        return [i for i in self.initiatives if i.status == "proposed"]
    
    def approve_improvement(self, initiative_id: str) -> bool:
        """Aprueba una iniciativa de mejora"""
        initiative = self._find_initiative(initiative_id)
        if initiative and initiative.status == "proposed":
            initiative.status = "approved"
            self._save_initiatives()
            return True
        return False
    
    def complete_improvement(self, initiative_id: str, 
                           results: Dict[str, Any]) -> bool:
        """Marca una iniciativa como completada"""
        initiative = self._find_initiative(initiative_id)
        if initiative and initiative.status == "in_progress":
            initiative.status = "completed"
            initiative.completed_at = datetime.now()
            initiative.results = results
            self._save_initiatives()
            return True
        return False
    
    def get_improvement_backlog(self) -> List[ImprovementInitiative]:
        """Obtiene el backlog de mejoras pendientes"""
        return [i for i in self.initiatives if i.status in ["proposed", "approved"]]
    
    def _find_initiative(self, initiative_id: str) -> Optional[ImprovementInitiative]:
        """Encuentra una iniciativa por ID"""
        for initiative in self.initiatives:
            if initiative.id == initiative_id:
                return initiative
        return None
    
    def _save_initiatives(self):
        """Guarda las iniciativas en almacenamiento persistente"""
        # Implementación específica de almacenamiento
        pass
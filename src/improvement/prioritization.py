from typing import Dict, List, Any
from datetime import datetime
import numpy as np

class ImprovementPrioritizer:
    """Sistema de priorización para iniciativas de mejora"""
    
    def __init__(self):
        self.prioritization_factors = {
            'impact': 0.4,
            'effort': 0.3,
            'urgency': 0.2,
            'strategic_alignment': 0.1
        }
    
    def prioritize_initiatives(self, initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioriza las iniciativas de mejora"""
        scored_initiatives = []
        
        for initiative in initiatives:
            score = self._calculate_score(initiative)
            scored_initiatives.append({
                **initiative,
                'priority_score': score
            })
        
        # Ordenar por score descendente
        return sorted(scored_initiatives, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_score(self, initiative: Dict[str, Any]) -> float:
        """Calcula el score de priorización para una iniciativa"""
        impact_score = self._rate_impact(initiative.get('impact', 'medium'))
        effort_score = self._rate_effort(initiative.get('effort', 'medium'))
        urgency_score = self._rate_urgency(initiative.get('urgency', 'medium'))
        strategic_score = self._rate_strategic_alignment(initiative.get('strategic_alignment', 0.5))
        
        weights = np.array([
            self.prioritization_factors['impact'],
            self.prioritization_factors['effort'],
            self.prioritization_factors['urgency'],
            self.prioritization_factors['strategic_alignment']
        ])
        
        scores = np.array([impact_score, effort_score, urgency_score, strategic_score])
        
        return np.dot(weights, scores)
    
    def _rate_impact(self, impact: str) -> float:
        """Califica el impacto de una iniciativa"""
        impact_scale = {
            'very_high': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'very_low': 0.2
        }
        return impact_scale.get(impact, 0.5)
    
    def _rate_effort(self, effort: str) -> float:
        """Califica el esfuerzo requerido (inverso)"""
        effort_scale = {
            'very_high': 0.2,
            'high': 0.4,
            'medium': 0.6,
            'low': 0.8,
            'very_low': 1.0
        }
        return effort_scale.get(effort, 0.5)
    
    def _rate_urgency(self, urgency: str) -> float:
        """Califica la urgencia de una iniciativa"""
        urgency_scale = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'none': 0.2
        }
        return urgency_scale.get(urgency, 0.5)
    
    def _rate_strategic_alignment(self, alignment: float) -> float:
        """Califica la alineación estratégica"""
        return max(0.0, min(1.0, alignment))
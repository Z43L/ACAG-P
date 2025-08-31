from typing import Dict, List, Any, Optional
import re
import logging

class KnowledgeValidator:
    """Valida que las respuestas estén basadas en conocimiento verificado"""
    
    def __init__(self, ncd_client):
        self.ncd_client = ncd_client
        self.logger = logging.getLogger(__name__)
        
    def validate_response(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una respuesta contra el conocimiento del NCD
        
        Returns:
            Dict con resultados de validación y respuesta mejorada
        """
        validation_result = {
            'is_valid': True,
            'confidence': 1.0,
            'issues': [],
            'suggested_improvements': [],
            'verified_sources': []
        }
        
        try:
            # Extraer afirmaciones de la respuesta
            claims = self._extract_claims(response)
            
            for claim in claims:
                claim_validation = self._validate_claim(claim, context)
                
                if not claim_validation['is_supported']:
                    validation_result['is_valid'] = False
                    validation_result['confidence'] *= 0.7
                    validation_result['issues'].append({
                        'claim': claim,
                        'reason': claim_validation['reason']
                    })
                    
                    # Sugerir mejora
                    if claim_validation.get('suggested_correction'):
                        validation_result['suggested_improvements'].append(
                            claim_validation['suggested_correction']
                        )
                        
                # Registrar fuentes verificadas
                validation_result['verified_sources'].extend(
                    claim_validation.get('sources', [])
                )
                
            # Mejorar respuesta si es necesario
            if validation_result['suggested_improvements']:
                response = self._enhance_response(
                    response, 
                    validation_result['suggested_improvements']
                )
                
            return {
                'validation_result': validation_result,
                'enhanced_response': response
            }
            
        except Exception as e:
            self.logger.error(f"Error en validación: {str(e)}")
            return {
                'validation_result': {
                    'is_valid': False,
                    'confidence': 0.0,
                    'issues': ['Error durante validación'],
                    'suggested_improvements': [],
                    'verified_sources': []
                },
                'enhanced_response': response
            }
            
    def _extract_claims(self, text: str) -> List[str]:
        """Extrae afirmaciones factuales del texto"""
        # Patrones para identificar afirmaciones
        patterns = [
            r'([^.!?]+(?:is|are|was|were|has|have)[^.!?]+[.!?])',
            r'([^.!?]+(?:can|will|should|must)[^.!?]+[.!?])',
            r'([^.!?]+(?:according to|based on|studies show)[^.!?]+[.!?])'
        ]
        
        claims = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims.extend(matches)
            
        return list(set(claims))  # Devolver únicos
        
    def _validate_claim(self, claim: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Valida una afirmación individual contra el conocimiento"""
        result = {
            'is_supported': False,
            'reason': 'Not validated',
            'sources': []
        }
        
        try:
            # Búsqueda semántica de la afirmación
            search_results = self.ncd_client.semantic_search(claim, top_k=3)
            
            if not search_results:
                result['reason'] = 'No supporting evidence found'
                return result
                
            # Verificar similitud con resultados
            max_similarity = max(result['score'] for result in search_results)
            
            if max_similarity < 0.6:
                result['reason'] = f'Weak similarity to knowledge (max: {max_similarity:.2f})'
                return result
                
            # La afirmación está respaldada
            result['is_supported'] = True
            result['reason'] = f'Supported by knowledge base (similarity: {max_similarity:.2f})'
            result['sources'] = [
                {'text': r['metadata'].get('text', ''), 'score': r['score']}
                for r in search_results
            ]
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error validando afirmación '{claim}': {str(e)}")
            result['reason'] = f'Validation error: {str(e)}'
            return result
            
    def _enhance_response(self, response: str, improvements: List[str]) -> str:
        """Mejora la respuesta basado en las validaciones"""
        # Implementación simple: añadir disclaimer
        if improvements:
            disclaimer = "\n\n*Nota: Esta respuesta ha sido mejorada basándose en verificación de conocimiento.*"
            return response + disclaimer
            
        return response
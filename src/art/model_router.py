from typing import Dict, Any, Optional, List
from enum import Enum
import openai
from transformers import pipeline
import torch
import logging

class ModelType(Enum):
    """Tipos de modelos disponibles"""
    LOCAL = "local"
    EXTERNAL = "external"
    HYBRID = "hybrid"

class QueryComplexity(Enum):
    """Niveles de complejidad de consultas"""
    SIMPLE = "simple"      # Consultas factuales directas
    COMPLEX = "complex"    # Consultas que requieren razonamiento
    CREATIVE = "creative"  # Consultas creativas o generativas

class ModelRouter:
    """Router inteligente para selección de modelos óptimos"""
    
    def __init__(self, local_model_path: str, openrouter_api_key: str):
        self.local_model = self._load_local_model(local_model_path)
        self.openrouter_client = self._setup_openrouter(openrouter_api_key)
        self.logger = logging.getLogger(__name__)
        self.cost_tracker = CostTracker()
        
    def _load_local_model(self, model_path: str):
        """Carga el modelo local especializado"""
        try:
            return pipeline(
                "text-generation",
                model=model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                max_length=512
            )
        except Exception as e:
            self.logger.error(f"Error cargando modelo local: {str(e)}")
            raise
            
    def _setup_openrouter(self, api_key: str):
        """Configura el cliente de OpenRouter"""
        return openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
    def analyze_query(self, query: str, context: Dict[str, Any]) -> QueryComplexity:
        """Analiza la complejidad de la consulta"""
        query_lower = query.lower()
        
        # Heurísticas para determinar complejidad
        simple_patterns = [
            r'^what (is|are)',
            r'^who (is|are)',
            r'^when (is|does)',
            r'^where (is|are)',
            r'^how (many|much)',
            r'^define',
            r'^list'
        ]
        
        complex_patterns = [
            r'^why',
            r'^how (does|do)',
            r'^explain',
            r'^compare',
            r'^analyze',
            r'^what (if|would)'
        ]
        
        creative_patterns = [
            r'^create',
            r'^write',
            r'^generate',
            r'^imagine',
            r'^tell (me|us) (a|the)',
            r'^make up'
        ]
        
        # Verificar patrones
        for pattern in creative_patterns:
            if re.match(pattern, query_lower):
                return QueryComplexity.CREATIVE
                
        for pattern in complex_patterns:
            if re.match(pattern, query_lower):
                return QueryComplexity.COMPLEX
                
        for pattern in simple_patterns:
            if re.match(pattern, query_lower):
                return QueryComplexity.SIMPLE
                
        # Por defecto, considerar compleja
        return QueryComplexity.COMPLEX
        
    def select_model(self, complexity: QueryComplexity, context: Dict[str, Any]) -> ModelType:
        """Selecciona el tipo de modelo basado en complejidad y contexto"""
        # Reglas de selección
        rules = {
            QueryComplexity.SIMPLE: ModelType.LOCAL,
            QueryComplexity.COMPLEX: ModelType.HYBRID,
            QueryComplexity.CREATIVE: ModelType.EXTERNAL
        }
        
        selected_type = rules[complexity]
        
        # Considerar restricciones de costo
        if self.cost_tracker.daily_cost > 10.0 and selected_type == ModelType.EXTERNAL:
            self.logger.warning("Límite de costo excedido, usando modelo local")
            return ModelType.LOCAL
            
        return selected_type
        
    def query_local_model(self, query: str, context: str = None) -> str:
        """Consulta el modelo local especializado"""
        prompt = self._build_local_prompt(query, context)
        
        try:
            response = self.local_model(
                prompt,
                max_new_tokens=256,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.local_model.tokenizer.eos_token_id
            )
            
            return response[0]['generated_text'].replace(prompt, '').strip()
            
        except Exception as e:
            self.logger.error(f"Error consultando modelo local: {str(e)}")
            raise
            
    def query_external_model(self, query: str, context: str = None) -> str:
        """Consulta modelos externos via OpenRouter"""
        messages = []
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Contexto: {context}"
            })
            
        messages.append({
            "role": "user",
            "content": query
        })
        
        try:
            response = self.openrouter_client.chat.completions.create(
                model="anthropic/claude-2",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            # Registrar costo
            self.cost_tracker.record_api_call(
                model="claude-2",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error consultando modelo externo: {str(e)}")
            raise
            
    def _build_local_prompt(self, query: str, context: str = None) -> str:
        """Construye el prompt para el modelo local"""
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"Contexto: {context}")
            
        prompt_parts.append(f"Consulta: {query}")
        prompt_parts.append("Respuesta:")
        
        return "\n".join(prompt_parts)
        
    def process_query(self, query: str, context: Dict[str, Any]) -> str:
        """Procesa una consulta completa usando el router"""
        complexity = self.analyze_query(query, context)
        model_type = self.select_model(complexity, context)
        
        context_str = self._format_context(context)
        
        if model_type == ModelType.LOCAL:
            return self.query_local_model(query, context_str)
            
        elif model_type == ModelType.EXTERNAL:
            return self.query_external_model(query, context_str)
            
        else:  # HYBRID
            # Primero intentar con local, luego validar y posiblemente usar externo
            local_response = self.query_local_model(query, context_str)
            confidence = self._calculate_confidence(local_response, query)
            
            if confidence >= 0.7:
                return local_response
            else:
                return self.query_external_model(query, context_str)
                
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formatea el contexto para uso en prompts"""
        context_parts = []
        
        if 'conversation_history' in context:
            history = context['conversation_history'][-3:]  # Últimas 3 interacciones
            for item in history:
                context_parts.append(f"Usuario: {item['query']}")
                context_parts.append(f"Asistente: {item['response']}")
                
        if 'knowledge_context' in context:
            knowledge = context['knowledge_context']
            if 'semantic_results' in knowledge:
                for result in knowledge['semantic_results'][:2]:
                    context_parts.append(f"Conocimiento relevante: {result['metadata'].get('text', '')}")
                    
        return "\n".join(context_parts)
        
    def _calculate_confidence(self, response: str, query: str) -> float:
        """Calcula la confianza en la respuesta (implementación simplificada)"""
        # Factores de confianza
        factors = {
            'length': min(len(response) / 100, 1.0),
            'specificity': self._calculate_specificity(response, query),
            'certainty_words': self._count_certainty_words(response)
        }
        
        # Ponderación
        weights = {
            'length': 0.3,
            'specificity': 0.4,
            'certainty_words': 0.3
        }
        
        confidence = sum(factors[factor] * weights[factor] for factor in factors)
        return min(confidence, 1.0)
        
    def _calculate_specificity(self, response: str, query: str) -> float:
        """Calcula qué tan específica es la respuesta respecto a la consulta"""
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        
        if not query_words:
            return 0.0
            
        overlap = query_words.intersection(response_words)
        return len(overlap) / len(query_words)
        
    def _count_certainty_words(self, text: str) -> float:
        """Cuenta palabras que indican certeza"""
        certainty_words = [
            'definitivamente', 'ciertamente', 'seguramente', 'exactamente',
            'precisamente', 'claramente', 'obviamente', 'indudablemente'
        ]
        
        text_lower = text.lower()
        count = sum(1 for word in certainty_words if word in text_lower)
        return min(count / 3, 1.0)  # Normalizar a 0-1
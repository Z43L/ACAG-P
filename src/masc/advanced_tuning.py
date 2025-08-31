from typing import Dict, Any
import torch
from torch.optim import AdamW
from transformers import get_linear_schedule_with_warmup

class AdvancedTuningStrategies:
    """Implementa estrategias avanzadas de fine-tuning para ACAG-P"""
    
    def __init__(self, model, train_dataloader, config: Dict[str, Any]):
        self.model = model
        self.train_dataloader = train_dataloader
        self.config = config
        
    def setup_optimizer(self) -> AdamW:
        """Configura el optimizador con decaimiento de peso"""
        no_decay = ["bias", "layer_norm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p for n, p in self.model.named_parameters()
                    if not any(nd in n for nd in no_decay) and p.requires_grad
                ],
                "weight_decay": self.config.get("weight_decay", 0.01),
            },
            {
                "params": [
                    p for n, p in self.model.named_parameters()
                    if any(nd in n for nd in no_decay) and p.requires_grad
                ],
                "weight_decay": 0.0,
            },
        ]
        
        return AdamW(
            optimizer_grouped_parameters,
            lr=self.config.get("learning_rate", 2e-4),
            eps=self.config.get("adam_epsilon", 1e-8)
        )
    
    def setup_scheduler(self, optimizer, total_steps: int):
        """Configura el programador de tasa de aprendizaje"""
        return get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.config.get("warmup_steps", 100),
            num_training_steps=total_steps
        )
    
    def apply_gradient_clipping(self, gradients, max_norm: float = 1.0):
        """Aplica gradient clipping para estabilizar el entrenamiento"""
        return torch.nn.utils.clip_grad_norm_(
            self.model.parameters(), max_norm
        )
    
    def dynamic_batch_scheduling(self, current_epoch: int) -> int:
        """Programación dinámica del tamaño de batch"""
        base_batch_size = self.config.get("base_batch_size", 4)
        
        # Aumentar batch size progresivamente
        if current_epoch > 5:
            return base_batch_size * 2
        elif current_epoch > 10:
            return base_batch_size * 4
        else:
            return base_batch_size
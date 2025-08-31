from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import torch
from typing import Dict, Any, List
import logging
import os

class QLoRATrainer:
    """Manejador de fine-tuning eficiente usando QLoRA"""
    
    def __init__(self, base_model_name: str = "huggingface.co/models/llama-7b",
                 output_dir: str = "./models/adapted"):
        self.base_model_name = base_model_name
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.tokenizer = None
        self.model = None
        
    def prepare_model(self, load_in_4bit: bool = True) -> Any:
        """Prepara el modelo para entrenamiento QLoRA"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                load_in_4bit=load_in_4bit,
                device_map="auto",
                torch_dtype=torch.float16,
                trust_remote_code=True
            )
            
            self.model = prepare_model_for_kbit_training(self.model)
            
            # Configuración LoRA
            lora_config = LoraConfig(
                r=8,
                lora_alpha=32,
                target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
                lora_dropout=0.05,
                bias="none",
                task_type="CAUSAL_LM"
            )
            
            self.model = get_peft_model(self.model, lora_config)
            self.model.print_trainable_parameters()
            
            return self.model
            
        except Exception as e:
            self.logger.error(f"Error preparando modelo: {str(e)}")
            raise
            
    def prepare_dataset(self, training_data: List[Dict]) -> Dataset:
        """Prepara el dataset para entrenamiento en formato instruction-response"""
        formatted_data = []
        
        for item in training_data:
            if 'instruction' in item and 'output' in item:
                text = f"### Instruction: {item['instruction']}\n\n### Response: {item['output']}"
                formatted_data.append({'text': text})
            elif 'question' in item and 'answer' in item:
                text = f"Question: {item['question']}\nAnswer: {item['answer']}"
                formatted_data.append({'text': text})
                
        return Dataset.from_list(formatted_data)
        
    def tokenize_function(self, examples):
        """Función de tokenización para el dataset"""
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding=False,
            max_length=512,
            return_tensors=None
        )
        
    def train(self, training_data: List[Dict], num_epochs: int = 3, 
             batch_size: int = 4) -> str:
        """Ejecuta el proceso de fine-tuning y devuelve la ruta del modelo resultante"""
        try:
            # Preparar modelo y datos
            model = self.prepare_model()
            dataset = self.prepare_dataset(training_data)
            tokenized_dataset = dataset.map(self.tokenize_function, batched=True)
            
            # Argumentos de entrenamiento optimizados para QLoRA
            training_args = TrainingArguments(
                output_dir=self.output_dir,
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                gradient_accumulation_steps=4,
                warmup_steps=100,
                learning_rate=2e-4,
                fp16=True,
                logging_steps=10,
                optim="paged_adamw_8bit",
                save_strategy="epoch",
                save_total_limit=2,
                report_to=None,
                max_grad_norm=0.3,
                lr_scheduler_type="cosine"
            )
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
            
            # Trainer
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator,
            )
            
            # Entrenamiento
            trainer.train()
            
            # Guardar modelo
            final_model_path = f"{self.output_dir}/acag-adapted-{datetime.now().strftime('%Y%m%d-%H%M')}"
            trainer.save_model(final_model_path)
            self.tokenizer.save_pretrained(final_model_path)
            
            self.logger.info(f"Fine-tuning completado. Modelo guardado en: {final_model_path}")
            return final_model_path
            
        except Exception as e:
            self.logger.error(f"Error en fine-tuning: {str(e)}")
            raise
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from typing import Dict, Any

class QLoRATuner:
    """Implementación del fine-tuning con QLoRA para ACAG-P"""
    
    def __init__(self, base_model_name: str, config: Dict[str, Any]):
        self.base_model_name = base_model_name
        self.config = config
        self.model = None
        self.tokenizer = None
        
    def _setup_quantization(self) -> BitsAndBytesConfig:
        """Configura la cuantización 4-bit"""
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True
        )
    
    def _setup_lora_config(self) -> LoraConfig:
        """Configura los parámetros de LoRA"""
        return LoraConfig(
            r=self.config.get("lora_rank", 8),
            lora_alpha=self.config.get("lora_alpha", 32),
            target_modules=self._get_target_modules(),
            lora_dropout=self.config.get("lora_dropout", 0.05),
            bias="none",
            task_type="CAUSAL_LM"
        )
    
    def _get_target_modules(self) -> List[str]:
        """Determina los módulos objetivo basado en la arquitectura del modelo"""
        model_architecture = self.config.get("model_architecture", "llama")
        
        if model_architecture == "llama":
            return ["q_proj", "v_proj", "k_proj", "o_proj"]
        elif model_architecture == "mistral":
            return ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj"]
        else:
            return ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"]
    
    def load_model(self) -> None:
        """Carga el modelo con configuración QLoRA"""
        quantization_config = self._setup_quantization()
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Preparar modelo para k-bit training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Aplicar configuración LoRA
        lora_config = self._setup_lora_config()
        self.model = get_peft_model(self.model, lora_config)
        
        print(f"Parámetros entrenables: {self.model.print_trainable_parameters()}")
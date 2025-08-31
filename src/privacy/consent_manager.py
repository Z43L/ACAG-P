from typing import Dict, List, Any
from enum import Enum
import hashlib

class ConsentType(Enum):
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    THIRD_PARTY_SHARING = "third_party_sharing"

class ConsentManager:
    """Gestiona el consentimiento del usuario para el procesamiento de datos"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.consent_types = [ct.value for ct in ConsentType]
        
    def initialize_user_consent(self, user_id: str) -> Dict[str, bool]:
        """Inicializa el registro de consentimiento para un nuevo usuario"""
        default_consent = {
            ConsentType.DATA_COLLECTION.value: False,
            ConsentType.DATA_PROCESSING.value: False,
            ConsentType.MODEL_TRAINING.value: False,
            ConsentType.THIRD_PARTY_SHARING.value: False
        }
        
        # Almacenar en base de datos
        self.db.store_consent(user_id, default_consent)
        return default_consent
        
    def get_consent(self, user_id: str) -> Dict[str, bool]:
        """Obtiene el estado de consentimiento actual del usuario"""
        return self.db.retrieve_consent(user_id) or self.initialize_user_consent(user_id)
        
    def update_consent(self, user_id: str, consent_type: ConsentType, 
                     granted: bool) -> bool:
        """Actualiza el consentimiento para un tipo específico"""
        current_consent = self.get_consent(user_id)
        current_consent[consent_type.value] = granted
        
        # Registrar el cambio con timestamp
        self.db.store_consent(user_id, current_consent)
        self.db.log_consent_change(user_id, consent_type.value, granted)
        
        return True
        
    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """Verifica si el usuario ha dado consentimiento para un tipo específico"""
        consent = self.get_consent(user_id)
        return consent.get(consent_type.value, False)
        
    def process_data_with_consent(self, user_id: str, data: Any, 
                                operation: ConsentType) -> Any:
        """Procesa datos solo si hay consentimiento adecuado"""
        if not self.check_consent(user_id, operation):
            raise ConsentError(f"Consentimiento requerido para {operation.value}")
            
        # Aplicar anonimización si es necesario
        if operation == ConsentType.DATA_PROCESSING:
            data = self.anonymize_data(data, user_id)
            
        return data
        
    def anonymize_data(self, data: Any, user_id: str) -> Any:
        """Anonimiza datos removiendo identificadores personales"""
        if isinstance(data, str):
            # Eliminar emails, números de teléfono, etc.
            data = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', '[EMAIL]', data)
            data = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', data)
            
        elif isinstance(data, dict):
            # Anonimizar campos específicos
            sensitive_fields = ['email', 'phone', 'address', 'credit_card']
            for field in sensitive_fields:
                if field in data:
                    data[field] = f'[ANONYMIZED_{field.upper()}]'
                    
        return data
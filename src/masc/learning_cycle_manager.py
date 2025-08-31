import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

class LearningCycleManager:
    """Gestiona el ciclo continuo de aprendizaje del MASC"""
    
    def __init__(self, ncd_client, art_client, data_generator, fine_tuner):
        self.ncd_client = ncd_client
        self.art_client = art_client
        self.data_generator = data_generator
        self.fine_tuner = fine_tuner
        self.last_training_time = datetime.now()
        self.training_interval = timedelta(hours=24)  # Entrenar cada 24 horas
        
    def should_trigger_training(self) -> bool:
        """Determina si es momento de ejecutar entrenamiento"""
        time_since_last = datetime.now() - self.last_training_time
        return time_since_last >= self.training_interval
        
    def get_new_knowledge(self, since: datetime) -> List[Dict]:
        """Obtiene conocimiento nuevo desde el timestamp especificado"""
        # Esta es una implementación simplificada
        # En producción, necesitaríamos una forma de consultar conocimiento reciente
        return []  # Placeholder
        
    def get_recent_conversations(self, since: datetime) -> List[Dict]:
        """Obtiene conversaciones recientes desde el timestamp especificado"""
        # Implementación específica dependiendo de cómo se almacenen las conversaciones
        return []  # Placeholder
        
    def execute_learning_cycle(self) -> bool:
        """Ejecuta un ciclo completo de aprendizaje"""
        if not self.should_trigger_training():
            return False
            
        try:
            # Obtener nuevos datos
            new_knowledge = self.get_new_knowledge(self.last_training_time)
            recent_conversations = self.get_recent_conversations(self.last_training_time)
            
            # Generar datos de entrenamiento
            training_data = []
            
            # De conocimiento nuevo
            for knowledge in new_knowledge:
                qa_pairs = self.data_generator.generate_qa_pairs(knowledge)
                training_data.extend(qa_pairs)
                
            # De conversaciones
            conversation_data = self.data_generator.generate_from_conversations(recent_conversations)
            training_data.extend(conversation_data)
            
            if not training_data:
                print("No new training data available")
                return False
                
            # Ejecutar fine-tuning
            model_path = self.fine_tuner.train(training_data)
            
            # Actualizar modelo en ART
            self.art_client.update_model(model_path)
            
            # Actualizar timestamp
            self.last_training_time = datetime.now()
            
            print(f"Learning cycle completed successfully. Model updated: {model_path}")
            return True
            
        except Exception as e:
            print(f"Error in learning cycle: {str(e)}")
            return False
            
    def start_continuous_learning(self):
        """Inicia el ciclo continuo de aprendizaje"""
        # Programar ejecución regular
        schedule.every(1).hours.do(self.check_and_train)
        
        print("Continuous learning started...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check cada minuto
            
    def check_and_train(self):
        """Verifica y ejecuta entrenamiento si es necesario"""
        if self.should_trigger_training():
            self.execute_learning_cycle()
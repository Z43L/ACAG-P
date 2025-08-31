import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import logging

class LearningScheduler:
    """Programa y gestiona los ciclos de aprendizaje automático"""
    
    def __init__(self, masc_module, config: Dict[str, Any]):
        self.masc = masc_module
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_training_time = None
        
    def should_trigger_training(self) -> bool:
        """Determina si es momento de ejecutar un ciclo de entrenamiento"""
        if not self.last_training_time:
            return True
        
        time_since_last = datetime.now() - self.last_training_time
        training_interval = timedelta(
            hours=self.config.get("training_interval_hours", 24)
        )
        
        return time_since_last >= training_interval
    
    def execute_learning_cycle(self) -> Dict[str, Any]:
        """Ejecuta un ciclo completo de aprendizaje"""
        if not self.should_trigger_training():
            return {"status": "skipped", "reason": "too_soon"}
        
        try:
            # 1. Recopilar nuevos datos
            new_knowledge = self._get_new_knowledge()
            recent_conversations = self._get_recent_conversations()
            
            # 2. Generar datos de entrenamiento
            training_data = self._generate_training_data(new_knowledge, recent_conversations)
            
            if len(training_data) < self.config.get("min_training_samples", 100):
                return {"status": "skipped", "reason": "insufficient_data"}
            
            # 3. Ejecutar fine-tuning
            training_result = self.masc.fine_tuner.train(
                training_data,
                num_epochs=self.config.get("training_epochs", 3),
                batch_size=self.config.get("batch_size", 4)
            )
            
            # 4. Evaluar el nuevo modelo
            evaluation_result = self.masc.evaluator.compare_models(
                self.masc.art_client.get_model_path(),
                training_result["model_path"],
                training_data[:100]  # Subconjunto para evaluación
            )
            
            # 5. Desplegar si hay mejora significativa
            if evaluation_result.get("should_deploy", False):
                deployment_success = self.masc.deployment_manager.deploy_model(
                    training_result["model_path"], evaluation_result
                )
                
                if deployment_success:
                    self.last_training_time = datetime.now()
                    return {
                        "status": "success",
                        "training_result": training_result,
                        "evaluation_result": evaluation_result
                    }
            
            return {
                "status": "success_no_deploy",
                "evaluation_result": evaluation_result
            }
            
        except Exception as e:
            self.logger.error(f"Error en ciclo de aprendizaje: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def start_continuous_learning(self):
        """Inicia el ciclo continuo de aprendizaje"""
        def learning_job():
            result = self.execute_learning_cycle()
            self.logger.info(f"Ciclo de aprendizaje completado: {result['status']}")
        
        # Programar ejecución regular
        schedule.every(1).hours.do(learning_job)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
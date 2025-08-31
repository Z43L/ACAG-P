from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging
import time

class LearningCycleManager:
    """Gestiona el ciclo completo de aprendizaje automático"""
    
    def __init__(self, ncd_client, art_client, config: Dict[str, Any] = None):
        self.ncd_client = ncd_client
        self.art_client = art_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        self.data_generator = SyntheticDataGenerator(ncd_client)
        self.fine_tuner = QLoRATrainer()
        self.evaluator = ModelEvaluator()
        self.deployment_manager = DeploymentManager(art_client)
        
        self.last_learning_cycle = None
        self.cycle_count = 0
        
    def execute_learning_cycle(self) -> Dict[str, Any]:
        """Ejecuta un ciclo completo de aprendizaje"""
        cycle_start = datetime.now()
        cycle_results = {
            'start_time': cycle_start.isoformat(),
            'success': False,
            'steps': {},
            'metrics': {}
        }
        
        try:
            # Paso 1: Recopilar nuevos datos
            new_knowledge = self.data_generator.get_new_knowledge(
                self.last_learning_cycle or datetime.now() - timedelta(days=7)
            )
            cycle_results['steps']['data_collection'] = {
                'samples_collected': len(new_knowledge),
                'success': True
            }
            
            # Paso 2: Generar datos de entrenamiento
            training_data = []
            for knowledge in new_knowledge:
                qa_pairs = self.data_generator.generate_qa_pairs(knowledge)
                training_data.extend(qa_pairs)
                
            if len(training_data) < self.config.get('min_training_samples', 50):
                cycle_results['steps']['training_generation'] = {
                    'success': False,
                    'reason': 'Insufficient training data',
                    'samples_generated': len(training_data)
                }
                return cycle_results
                
            cycle_results['steps']['training_generation'] = {
                'samples_generated': len(training_data),
                'success': True
            }
            
            # Paso 3: Fine-tuning del modelo
            model_path = self.fine_tuner.train(
                training_data,
                num_epochs=self.config.get('training_epochs', 3),
                batch_size=self.config.get('batch_size', 4)
            )
            cycle_results['steps']['fine_tuning'] = {
                'model_path': model_path,
                'success': True
            }
            
            # Paso 4: Evaluación del modelo
            evaluation_results = self.evaluator.compare_models(
                self.art_client.get_model_path(),
                model_path,
                training_data[:100]  # Usar subset para evaluación
            )
            cycle_results['steps']['evaluation'] = evaluation_results
            
            # Paso 5: Despliegue condicional
            if evaluation_results.get('should_deploy', False):
                deployment_success = self.deployment_manager.deploy_model(
                    model_path, evaluation_results
                )
                cycle_results['steps']['deployment'] = {
                    'success': deployment_success,
                    'model_deployed': model_path if deployment_success else None
                }
            else:
                cycle_results['steps']['deployment'] = {
                    'success': False,
                    'reason': 'Insufficient improvement',
                    'improvement_score': evaluation_results.get('total_improvement', 0)
                }
                
            # Actualizar estado
            self.last_learning_cycle = cycle_start
            self.cycle_count += 1
            cycle_results['success'] = True
            cycle_results['end_time'] = datetime.now().isoformat()
            
            self.logger.info(f"Ciclo de aprendizaje #{self.cycle_count} completado exitosamente")
            
        except Exception as e:
            cycle_results['success'] = False
            cycle_results['error'] = str(e)
            cycle_results['end_time'] = datetime.now().isoformat()
            self.logger.error(f"Error en ciclo de aprendizaje: {str(e)}")
            
        return cycle_results
        
    def get_learning_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del aprendizaje"""
        return {
            'total_cycles': self.cycle_count,
            'last_cycle': self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
            'successful_cycles': self.cycle_count,  # Se implementaría tracking real
            'average_improvement': 0.15,  # Placeholder
            'models_deployed': self.cycle_count
        }
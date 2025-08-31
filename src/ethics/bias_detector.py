from typing import Dict, List, Any
import pandas as pd
from sklearn.metrics import fairness_metrics

class BiasDetector:
    """Detecta y mitiga sesgos en los modelos y datos"""
    
    def __init__(self):
        self.sensitive_attributes = ['gender', 'ethnicity', 'age', 'location']
        
    def detect_data_bias(self, dataset: pd.DataFrame) -> Dict[str, float]:
        """Detecta sesgos en los datos de entrenamiento"""
        bias_metrics = {}
        
        for attribute in self.sensitive_attributes:
            if attribute in dataset.columns:
                # Calcular representación proporcional
                value_counts = dataset[attribute].value_counts(normalize=True)
                bias_score = self._calculate_bias_score(value_counts)
                bias_metrics[f'data_bias_{attribute}'] = bias_score
                
        return bias_metrics
        
    def detect_model_bias(self, model, X_test: pd.DataFrame, 
                         y_test: pd.Series) -> Dict[str, float]:
        """Detecta sesgos en las predicciones del modelo"""
        predictions = model.predict(X_test)
        bias_metrics = {}
        
        for attribute in self.sensitive_attributes:
            if attribute in X_test.columns:
                # Calcular métricas de equidad
                fairness_report = fairness_metrics(
                    y_true=y_test,
                    y_pred=predictions,
                    sensitive_features=X_test[attribute]
                )
                bias_metrics[f'model_bias_{attribute}'] = fairness_report
                
        return bias_metrics
        
    def mitigate_bias(self, dataset: pd.DataFrame, 
                     bias_metrics: Dict[str, float]) -> pd.DataFrame:
        """Aplica técnicas de mitigación de sesgos"""
        mitigated_dataset = dataset.copy()
        
        for attribute, bias_score in bias_metrics.items():
            if bias_score > 0.1:  # Umbral de sesgo significativo
                # Aplicar re-muestreo para balancear representación
                mitigated_dataset = self._apply_resampling(mitigated_dataset, attribute)
                
        return mitigated_dataset
        
    def _calculate_bias_score(self, value_counts: pd.Series) -> float:
        """Calcula un score de sesgo basado en la distribución"""
        # Score de 0 (perfectamente balanceado) a 1 (completamente sesgado)
        return 1 - value_counts.min() / value_counts.max()
        
    def _apply_resampling(self, dataset: pd.DataFrame, attribute: str) -> pd.DataFrame:
        """Aplica re-muestreo para balancear grupos subrepresentados"""
        # Implementación de re-muestreo preferencial
        group_sizes = dataset[attribute].value_counts()
        target_size = group_sizes.max()
        
        balanced_groups = []
        for group_name, group_data in dataset.groupby(attribute):
            if len(group_data) < target_size:
                # Sobremuestrear grupo minoritario
                oversampled = group_data.sample(
                    target_size - len(group_data), 
                    replace=True, 
                    random_state=42
                )
                balanced_groups.append(pd.concat([group_data, oversampled]))
            else:
                balanced_groups.append(group_data)
                
        return pd.concat(balanced_groups)
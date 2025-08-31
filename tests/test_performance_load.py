import pytest
import time
from unittest.mock import patch
from tests.load_test import LoadTester

class TestPerformanceAndLoad:
    """Pruebas de rendimiento y carga del sistema ACAG-P"""
    
    @pytest.mark.load
    @patch('aiohttp.ClientSession.post')
    def test_load_performance(self, mock_post):
        """Prueba de rendimiento bajo carga"""
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json.return_value = {'response': 'Test response'}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        tester = LoadTester("http://localhost:8000", concurrent_users=10, duration=10)
        
        start_time = time.time()
        results = asyncio.run(tester.run_test())
        end_time = time.time()
        
        # Verificar que el throughput sea aceptable
        throughput = len(results) / (end_time - start_time)
        assert throughput >= 2.0  # Al menos 2 queries por segundo
        
        # Verificar que la tasa de error sea baja
        successful = sum(1 for r in results if r['success'])
        error_rate = (len(results) - successful) / len(results)
        assert error_rate <= 0.01  # Máximo 1% de errores
    
    @pytest.mark.performance
    def test_response_time_percentiles(self):
        """Prueba percentiles de tiempo de respuesta"""
        # Simular resultados de pruebas de carga
        test_results = [
            {'response_time': 0.1, 'success': True},
            {'response_time': 0.2, 'success': True},
            {'response_time': 0.15, 'success': True},
            {'response_time': 0.3, 'success': True},
            {'response_time': 0.25, 'success': True},
            {'response_time': 0.12, 'success': True},
            {'response_time': 0.18, 'success': True},
            {'response_time': 0.22, 'success': True},
            {'response_time': 0.28, 'success': True},
            {'response_time': 0.35, 'success': True},
        ]
        
        response_times = [r['response_time'] for r in test_results if r['success']]
        response_times.sort()
        
        # Calcular percentiles
        p50 = response_times[int(len(response_times) * 0.5)]
        p90 = response_times[int(len(response_times) * 0.9)]
        p95 = response_times[int(len(response_times) * 0.95)]
        
        assert p50 <= 0.25  # Percentil 50 bajo 250ms
        assert p90 <= 0.32   # Percentil 90 bajo 320ms
        assert p95 <= 0.35   # Percentil 95 bajo 350ms
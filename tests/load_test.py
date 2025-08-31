#!/usr/bin/env python3
"""
Pruebas de carga y rendimiento para ACAG-P
"""

import asyncio
import aiohttp
import time
from datetime import datetime
import statistics

class LoadTester:
    def __init__(self, base_url: str, concurrent_users: int = 10, duration: int = 60):
        self.base_url = base_url
        self.concurrent_users = concurrent_users
        self.duration = duration
        self.results = []
        
    async def run_test(self):
        """Ejecuta la prueba de carga"""
        start_time = time.time()
        tasks = []
        
        for i in range(self.concurrent_users):
            task = asyncio.create_task(self.simulate_user(f"user_{i}"))
            tasks.append(task)
        
        # Ejecutar por el tiempo especificado
        await asyncio.sleep(self.duration)
        
        # Cancelar todas las tareas
        for task in tasks:
            task.cancel()
        
        # Esperar a que todas las tareas se cancelen
        await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        self.analyze_results(start_time, end_time)
    
    async def simulate_user(self, user_id: str):
        """Simula un usuario realizando consultas"""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    start = time.time()
                    
                    # Consulta típica
                    query = {
                        "query": "Explain artificial intelligence and its applications",
                        "user_id": user_id,
                        "context": {}
                    }
                    
                    async with session.post(
                        f"{self.base_url}/api/query",
                        json=query,
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            end = time.time()
                            self.results.append({
                                'user_id': user_id,
                                'response_time': end - start,
                                'success': True,
                                'timestamp': datetime.now()
                            })
                        else:
                            self.results.append({
                                'user_id': user_id,
                                'response_time': 0,
                                'success': False,
                                'timestamp': datetime.now()
                            })
                    
                    # Esperar entre consultas
                    await asyncio.sleep(2)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.results.append({
                        'user_id': user_id,
                        'response_time': 0,
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now()
                    })
                    await asyncio.sleep(1)
    
    def analyze_results(self, start_time: float, end_time: float):
        """Analiza los resultados de la prueba"""
        total_time = end_time - start_time
        successful_requests = [r for r in self.results if r['success']]
        failed_requests = [r for r in self.results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        print(f"📊 Resultados de la prueba de carga:")
        print(f"   Duración: {total_time:.2f} segundos")
        print(f"   Usuarios concurrentes: {self.concurrent_users}")
        print(f"   Total requests: {len(self.results)}")
        print(f"   Requests exitosos: {len(successful_requests)}")
        print(f"   Requests fallidos: {len(failed_requests)}")
        print(f"   Tasa de éxito: {(len(successful_requests)/len(self.results))*100:.2f}%")
        print(f"   Throughput: {len(self.results)/total_time:.2f} requests/segundo")
        print(f"   Response time promedio: {statistics.mean(response_times)*1000:.2f} ms")
        print(f"   Response time p95: {statistics.quantiles(response_times, n=100)[94]*1000:.2f} ms")
        print(f"   Response time máximo: {max(response_times)*1000:.2f} ms")

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    users = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    duration = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    
    tester = LoadTester(base_url, users, duration)
    asyncio.run(tester.run_test())
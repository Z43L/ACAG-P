import pinecone
from typing import Dict, List, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

class PineconeManager:
    """Gestor de la base de datos vectorial Pinecone para ACAG-P"""
    
    def __init__(self, api_key: str, environment: str, index_name: str = "acag-knowledge"):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.logger = logging.getLogger(__name__)
        self.embedding_model = None
        
        self._initialize_pinecone()
        self._load_embedding_model()
        
    def _initialize_pinecone(self) -> None:
        """Inicializa la conexión con Pinecone"""
        try:
            pinecone.init(api_key=self.api_key, environment=self.environment)
            
            # Crear índice si no existe
            if self.index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimensión para all-MiniLM-L6-v2
                    metric="cosine",
                    spec=pinecone.Spec(
                        serverless=pinecone.ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                )
                self.logger.info(f"Índice Pinecone '{self.index_name}' creado")
                
            self.index = pinecone.Index(self.index_name)
            self.logger.info("Pinecone inicializado correctamente")
            
        except Exception as e:
            self.logger.error(f"Error inicializando Pinecone: {str(e)}")
            raise
            
    def _load_embedding_model(self) -> None:
        """Carga el modelo de embeddings para ACAG-P"""
        try:
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            self.logger.info("Modelo de embeddings cargado correctamente")
        except Exception as e:
            self.logger.error(f"Error cargando modelo de embeddings: {str(e)}")
            raise
            
    def generate_embeddings(self, text: str) -> np.ndarray:
        """Genera embeddings para texto usando el modelo configurado"""
        if not self.embedding_model:
            raise ValueError("Modelo de embeddings no inicializado")
            
        return self.embedding_model.encode(text).astype(np.float32)
        
    def upsert_vectors(self, vectors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Inserta o actualiza vectores en Pinecone"""
        try:
            pinecone_vectors = []
            for vec in vectors:
                pinecone_vectors.append({
                    "id": vec["id"],
                    "values": vec["embeddings"],
                    "metadata": vec.get("metadata", {})
                })
                
            result = self.index.upsert(vectors=pinecone_vectors)
            self.logger.info(f"Vectores upserted: {result['upserted_count']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error upserting vectores: {str(e)}")
            raise
            
    def semantic_search(self, query: str, top_k: int = 5, 
                      filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Realiza búsqueda semántica por similitud"""
        try:
            # Generar embedding para la consulta
            query_embedding = self.generate_embeddings(query).tolist()
            
            # Ejecutar búsqueda
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filters
            )
            
            return [{
                "id": match["id"],
                "score": match["score"],
                "metadata": match["metadata"]
            } for match in results["matches"]]
            
        except Exception as e:
            self.logger.error(f"Error en búsqueda semántica: {str(e)}")
            raise
            
    def get_index_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del índice"""
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            self.logger.error(f"Error obteniendo stats del índice: {str(e)}")
            raise
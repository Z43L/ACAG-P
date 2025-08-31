from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """Configuración principal de la aplicación ACAG-P"""
    
    # Base de datos
    neo4j_uri: str = Field(..., env='NEO4J_URI')
    neo4j_user: str = Field(..., env='NEO4J_USER')
    neo4j_password: str = Field(..., env='NEO4J_PASSWORD')
    
    pinecone_api_key: str = Field(..., env='PINECONE_API_KEY')
    pinecone_environment: str = Field(..., env='PINECONE_ENVIRONMENT')
    pinecone_index: str = Field(..., env='PINECONE_INDEX')
    
    redis_url: str = Field(..., env='REDIS_URL')
    
    # OpenRouter
    openrouter_api_key: str = Field(..., env='OPENROUTER_API_KEY')
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", env='OPENROUTER_BASE_URL')
    
    # Modelos locales
    local_model_path: str = Field("./models/llama-7b", env='LOCAL_MODEL_PATH')
    embedding_model: str = Field("sentence-transformers/all-MiniLM-L6-v2", env='EMBEDDING_MODEL')
    
    # Configuración de la aplicación
    app_port: int = Field(8000, env='APP_PORT')
    app_host: str = Field("0.0.0.0", env='APP_HOST')
    debug: bool = Field(False, env='DEBUG')
    
    # Configuración de fine-tuning
    training_batch_size: int = Field(4, env='TRAINING_BATCH_SIZE')
    training_epochs: int = Field(3, env='TRAINING_EPOCHS')
    learning_rate: float = Field(2e-4, env='LEARNING_RATE')
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()
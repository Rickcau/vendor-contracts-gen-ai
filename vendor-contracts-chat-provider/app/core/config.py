from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Vendor Contracts Chat Provider"
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4"
    OPENAI_API_VERSION: str = "2024-02-15-preview"
    
    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()
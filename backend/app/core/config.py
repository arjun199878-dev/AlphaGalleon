from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AlphaGalleon Brain"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Placeholder for Gemini API Key
    GOOGLE_API_KEY: str = ""

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

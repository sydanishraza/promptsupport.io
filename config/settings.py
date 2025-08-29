from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Core database and storage
    MONGO_URI: str = Field(default="mongodb://localhost:27017/promptsupport", description="Mongo connection string")
    MONGO_URL: str = Field(default="mongodb://localhost:27017/", description="Legacy mongo URL")
    DATABASE_NAME: str = Field(default="promptsupport_db", description="Database name")
    UPLOAD_DIR: str = "static/uploads"
    TEMP_DIR: str = "temp_uploads"
    
    # LLM Configuration
    LLM_PROVIDER: str = "openai"   # or "anthropic"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    LOCAL_LLM_URL: str | None = None
    LOCAL_LLM_MODEL: str | None = None
    
    # Vector DB Configuration  
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: str = "6333"
    QDRANT_API_KEY: str | None = None
    
    # Other AI Services
    ASSEMBLYAI_API_KEY: str | None = None
    
    # Engine Flags
    ENABLE_V1: bool = False
    ENABLE_HYBRID: bool = False
    
    # KE-PR10.5: V2-Only Validation Flag
    FORCE_V2_ONLY: bool = Field(default=False, description="Force system to run exclusively on V2 engine modules")
    
    # KE-PR10.5: Legacy endpoint behavior
    LEGACY_ENDPOINT_BEHAVIOR: str = Field(default="warn", description="How to handle legacy endpoints: 'warn', 'block', 'disable'")

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra fields to prevent validation errors

settings = Settings()
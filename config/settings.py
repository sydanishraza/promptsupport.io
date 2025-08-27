from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    MONGO_URI: str = Field(default="mongodb://localhost:27017/promptsupport", description="Mongo connection string")
    UPLOAD_DIR: str = "static/uploads"
    TEMP_DIR: str = "temp_uploads"
    LLM_PROVIDER: str = "openai"   # or "anthropic"
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    ENABLE_V1: bool = False
    ENABLE_HYBRID: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_expire_minutes: int = 720
    ollama_host: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3.2:latest"
    ollama_embed_model: str = "nomic-embed-text"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    chroma_path: str = "./data/chroma"
    upload_dir: str = "./data/uploads"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


settings = Settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application Config
    PROJECT_NAME: str = "ChatPDF API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Config
    POSTGRES_USER: str = "chatpdf_user"
    POSTGRES_PASSWORD: str = "chatpdf_password"
    POSTGRES_HOST: str = "localhost" # Docker Compose 起動時はlocalhost
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "chatpdf_db"
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # async用ドライバ asyncpg ではなく同期版 psycopg2 を利用 (TDDと相性が良いため初期は同期で進める)
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Ollama Config
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()

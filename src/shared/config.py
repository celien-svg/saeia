from pydantic import BaseSettings, Field
class Settings(BaseSettings):
# ---------- PostgreSQL ----------
DB_HOST: str = Field(..., env="DB_HOST")
DB_PORT: int = Field(5432, env="DB_PORT")
DB_NAME: str = Field(..., env="DB_NAME")
DB_USER: str = Field(..., env="DB_USER")
DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
# ---------- Redis ----------
REDIS_HOST: str = Field(..., env="REDIS_HOST")
REDIS_PORT: int = Field(6379, env="REDIS_PORT")
# ---------- Vector DB ----------
VECTOR_DB_API_URL: str = Field(..., env="VECTOR_DB_API_URL")
VECTOR_EMBED_MODEL: str = Field(..., env="VECTOR_EMBED_MODEL")
# ---------- Ollama ----------
OLLAMA_HOST: str = Field(..., env="OLLAMA_HOST")
OLLAMA_MODEL: str = Field(..., env="OLLAMA_MODEL")
class Config:
env_prefix = "" # on n’utilise pas de préfixe dans le compose
case_sensitive = False
@property
def db_url(self) -> str:
"""PostgreSQL URL SQLAlchemy compatible."""
return (
f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
)
@property
def redis_url(self) -> str:
return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"
@property
def vector_db_url(self) -> str:
return self.VECTOR_DB_API_URL
@property
def ollama_host(self) -> str:
return self.OLLAMA_HOST
# Export d’une instance unique
settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de connexion au serveur Ollama, chargés depuis `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---------- Serveur Ollama ----------
    OLLAMA_HOST: str
    OLLAMA_VLM_MODEL: str
    
    # ---------- BDD postgresql ----------
    POSTGRES_HOST : str
    POSTGRES_PORT : int
    POSTGRES_USER : str
    POSTGRES_PASSWORD : str
    POSTGRES_DB : str

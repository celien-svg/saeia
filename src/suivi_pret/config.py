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


# Instance partagée de la configuration du projet.
settings = Settings()  # pyright: ignore[reportCallIssue]
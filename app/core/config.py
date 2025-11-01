# app/core/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, Field, AliasChoices, AliasPath


class Settings(BaseSettings):
    # app
    app_name: str = "semantic"
    app_env: str = "dev"  # dev | staging | prod

    # db
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "semantic"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # openai
    openai_api_key: str | None = Field(default=None,validation_alias=AliasChoices("OPENAI_API_KEY", "openai_api_key"))
    openai_embed_model: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field  # type: ignore[misc]
    @property
    def database_url(self) -> str:
        # postgresql+psycopg is the modern psycopg3 driver
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings, so env is read only once.
    """
    return Settings()

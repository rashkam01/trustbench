from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    database_url: str
    generation_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    retrieval_k: int = 5


settings = Settings()
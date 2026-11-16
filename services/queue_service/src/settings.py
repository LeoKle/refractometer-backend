from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    MONGO_DB_NAME: str = "refractometer-queue-service"

    MAX_ATTEMPTS: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Settings()

from pathlib import Path

import toml
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_version():
    version = None
    pyproject_toml_file = Path(__file__).parent.parent / "pyproject.toml"
    if pyproject_toml_file.exists() and pyproject_toml_file.is_file():
        data = toml.load(pyproject_toml_file)
        if "project" in data and "version" in data["project"]:
            version = data["project"]["version"]
        elif "tool" in data and "poetry" in data["tool"] and "version" in data["tool"]["poetry"]:
            version = data["tool"]["poetry"]["version"]

    return version


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    MONGO_DB_NAME: str = "refractometer"

    VERSION: str = get_version()

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


config = Settings()

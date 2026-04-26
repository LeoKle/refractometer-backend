import json
import os
from dotenv import load_dotenv


def get_version():
    try:
        with open("package.json", encoding="utf-8") as f:
            data = json.load(f)
            sem_version = data.get("version", "No version found")
            return sem_version
    except FileNotFoundError:
        return "0.0.0"


class Config:
    load_dotenv()
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "refractometer")
    VERSION = get_version()


config = Config()

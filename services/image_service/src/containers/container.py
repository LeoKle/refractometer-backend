from dependency_injector import containers, providers
from pymongo import MongoClient

from repositories.image_repository import ImageRepository
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(Settings())

    mongo_client = providers.Singleton(
        MongoClient,
        config.MONGO_URI,
    )

    mongo_database = providers.Singleton(
        lambda client, name: client[name],
        mongo_client,
        name=config.MONGO_DB_NAME,
    )

    image_repo = providers.Factory(ImageRepository, db=mongo_database)

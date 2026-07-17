from dependency_injector import containers, providers
from pymongo import MongoClient

from services.queue_service import QueueService
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

    queue_collection = providers.Singleton(
        lambda db: db["queue"],
        mongo_database,
    )

    queue_service = providers.Factory(
        QueueService,
        collection=queue_collection,
    )

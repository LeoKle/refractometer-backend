from dependency_injector import containers, providers
from pymongo import MongoClient


class MongoContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    mongo_client = providers.Singleton(
        MongoClient,
        config.MONGO_URI,
    )

    mongo_database = providers.Singleton(
        lambda client, name: client[name],
        mongo_client,
        name=config.MONGO_DB_NAME,
    )

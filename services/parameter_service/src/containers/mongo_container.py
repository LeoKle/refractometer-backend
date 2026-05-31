from dependency_injector import containers, providers
from pymongo import MongoClient

from repositories.sample_repository import SampleRepository
from repositories.spectrum_repository import SpectrumRepository


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

    sample_collection = providers.Singleton(
        lambda db: db["samples"],
        mongo_database,
    )

    sample_repository = providers.Factory(SampleRepository, collection=sample_collection)

    spectrum_collection = providers.Singleton(
        lambda db: db["spectrums"],
        mongo_database,
    )

    spectrum_repository = providers.Factory(SpectrumRepository, collection=spectrum_collection)

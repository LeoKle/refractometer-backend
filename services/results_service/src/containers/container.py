from dependency_injector import containers, providers
from pymongo import MongoClient

from repositories.simulation_repository import SimulationResultRepository
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

    sim_result_collection = providers.Singleton(
        lambda db: db["results"],
        mongo_database,
    )

    sim_result_repository = providers.Factory(
        SimulationResultRepository, collection=sim_result_collection
    )

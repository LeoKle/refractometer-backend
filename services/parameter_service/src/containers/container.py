from dependency_injector import containers, providers

from containers import mongo_container
from services.sample_service import SampleService
from services.spectrum_service import SpectrumService
from settings import Settings


class DependencyContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_pydantic(Settings())

    mongo_container = providers.Container(mongo_container.MongoContainer, config=config)

    sample_service = providers.Factory(SampleService, repository=mongo_container.sample_repository)
    spectrum_service = providers.Factory(
        SpectrumService, repository=mongo_container.spectrum_repository
    )

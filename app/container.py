from dependency_injector import containers, providers

from app.services.google_sso_service import GoogleAuthService
from settings import Settings


class AppContainer(containers.DeclarativeContainer):
    settings: Settings = providers.Singleton(
        Settings,
        _env_file=".env"
    )
    google_auth_service: GoogleAuthService = providers.Singleton(
        GoogleAuthService,
        settings=settings
    )

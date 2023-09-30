from dependency_injector import containers, providers

from app.services.google_sso_service import GoogleAuthService
from app.services.user_permissions import UserPermissionSheet, UserPermissionStore
from settings import Settings


class AppContainer(containers.DeclarativeContainer):
    settings: Settings = providers.Singleton(
        Settings,
        _env_file="keys/.env"
    )
    google_auth_service: GoogleAuthService = providers.Singleton(
        GoogleAuthService,
        settings=settings
    )

    user_permission_store: UserPermissionStore = providers.Factory(UserPermissionStore)
    user_permission_sheet: UserPermissionSheet = providers.Factory(
        UserPermissionSheet,
        store=user_permission_store,
        settings=settings
    )

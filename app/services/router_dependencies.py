from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
import requests
from app.container import AppContainer
from app.services.google_sso_service import GoogleAuthService
from jose import jwt

from app.services.models import User
from app.services.user_permissions import UserPermissionSheet, UserPermissionStore
from settings import Settings


@inject
def generate_token(
        code: str,
        google_oauth_service: GoogleAuthService = Provide[AppContainer.google_auth_service],
        settings: Settings = Provide[AppContainer.settings],
        user_permission_store: UserPermissionStore = Provide[AppContainer.user_permission_store]
) -> dict:
    response_token_data = google_oauth_service.fetch_access_and_refresh_tokens_for_login_response_obj(code)
    verify_access_token_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={response_token_data['access_token']}"
    response_user_data = requests.get(verify_access_token_url).json()
    email_username, _ = response_user_data['email'].split("@")
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_time)
    token_payload = {"sub": email_username, "exp": expire,
                     "data": user_permission_store.fetch_one(item_id=response_user_data['email'])}
    with open(settings.private_key_path, 'r') as f:
        private_key = f.read()
    token = jwt.encode(token_payload, private_key, algorithm='RS512')
    return {"token": token}


@inject
def fetch_flow_auth_url(
        redirect_url: str,
        google_oauth_service: GoogleAuthService = Provide[AppContainer.google_auth_service]
) -> str:
    return google_oauth_service.fetch_flow_auth_url(redirect_url)


@inject
def spreadsheet_sync(
        user_permission_sheet: UserPermissionSheet = Provide[AppContainer.user_permission_sheet]
) -> None:
    user_permission_sheet.synchronize()


@inject
def fetch_all_db_data(user_permission_store: UserPermissionStore = Provide[AppContainer.user_permission_store]) -> list[
    User]:
    return user_permission_store.fetch()

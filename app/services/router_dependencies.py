from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
import requests
from app.container import AppContainer
from app.services.google_sso_service import GoogleAuthService
from jose import jwt

from settings import Settings


@inject
def generate_token(
        code: str,
        google_oauth_service: GoogleAuthService = Provide[AppContainer.google_auth_service],
        settings: Settings = Provide[AppContainer.settings]
) -> dict:
    response_token_data = google_oauth_service.fetch_access_and_refresh_tokens_for_login_response_obj(code)
    verify_access_token_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={response_token_data['access_token']}"
    response_user_data = requests.get(verify_access_token_url).json()
    email_username, _ = response_user_data['email'].split("@")
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expire_time)
    token_payload = {"sub": email_username, "exp": expire}
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

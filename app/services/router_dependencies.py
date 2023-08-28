from dependency_injector.wiring import Provide, inject
import requests
from app.container import AppContainer
from app.services.google_sso_service import GoogleAuthService


@inject
def fetch_userinfo_from_id_token(
        code: str,
        google_oauth_service: GoogleAuthService = Provide[AppContainer.google_auth_service]
) -> dict:
    response_token_data = google_oauth_service.fetch_access_and_refresh_tokens_for_login_response_obj(code)
    verify_access_token_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={response_token_data['access_token']}"
    response_user_data = requests.get(verify_access_token_url).json()
    return {**response_token_data, **response_user_data}


@inject
def fetch_flow_auth_url(
        google_oauth_service: GoogleAuthService = Provide[AppContainer.google_auth_service]
) -> str:
    return google_oauth_service.fetch_flow_auth_url()

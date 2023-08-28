import json

import requests

from settings import Settings
import google_auth_oauthlib.flow


class GoogleAuthService:
    def __init__(self, settings: Settings):
        self.base_settings = settings

    def get_flow_credentials(self) -> dict:
        return {
            "web": {
                "client_id": self.base_settings.client_id,
                "client_secret": self.base_settings.client_secret,
                "redirect_uris": self.base_settings.redirect_uris,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
            }
        }

    def fetch_flow_auth_url(self) -> str:
        flow = google_auth_oauthlib.flow.Flow.from_client_config(
            self.get_flow_credentials(),
            scopes=[
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid",
            ],
        )

        flow.redirect_uri = "http://localhost:3000/google-sso/set-token"
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return authorization_url

    def fetch_access_and_refresh_tokens_for_login_response_obj(self, code: str) -> dict:
        request_body = {
            "client_id": self.base_settings.client_id,
            "client_secret": self.base_settings.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": "http://localhost:3000/google-sso/set-token"
        }
        fetch_token_url = "https://oauth2.googleapis.com/token"
        response_token_data = requests.post(
            fetch_token_url, json.dumps(request_body)
        ).json()
        return response_token_data

    @staticmethod
    def parse_email_from_token(access_token: str) -> str:
        verify_access_token_url = (
            f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        )
        response_email = requests.get(verify_access_token_url).json().get("email")

        if response_email is None:
            raise Exception("invalid access token")

        return response_email

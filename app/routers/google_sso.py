from fastapi import APIRouter
from starlette.responses import RedirectResponse

from app.services.router_dependencies import fetch_userinfo_from_id_token, fetch_flow_auth_url

router = APIRouter(prefix="/google-sso")


@router.get("/create-auth-link", tags=["oauth"])
def create_authentication_link():
    return RedirectResponse(url=fetch_flow_auth_url(), status_code=307)


@router.get("/set-token", tags=["oauth"])
def fetch_access_and_refresh_tokens_for_login(code: str) -> dict:
    return fetch_userinfo_from_id_token(code)

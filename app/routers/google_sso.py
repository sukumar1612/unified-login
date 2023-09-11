from requests.models import PreparedRequest
from fastapi import APIRouter, Query
from starlette.responses import RedirectResponse

from app.services.router_dependencies import generate_token, fetch_flow_auth_url

router = APIRouter(prefix="/google-sso")


@router.get("/create-auth-link", tags=["oauth"])
def create_authentication_link(redirect_url: str = Query()):
    return RedirectResponse(url=fetch_flow_auth_url(redirect_url), status_code=307)


@router.get("/set-token", tags=["oauth"])
def fetch_access_and_refresh_tokens_for_login(state: str = Query(), code: str = Query()):
    redirect_url = state
    jwt = generate_token(code)
    req = PreparedRequest()
    req.prepare_url(redirect_url, jwt)
    return RedirectResponse(url=req.url, status_code=307)

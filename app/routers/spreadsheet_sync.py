from fastapi import APIRouter
from starlette.responses import Response

from app.services.router_dependencies import spreadsheet_sync, fetch_all_db_data

router = APIRouter(prefix="/spreadsheet")


@router.get("/sync", tags=["spreadsheet"])
def spreadsheet_sync_endpoint():
    spreadsheet_sync()
    return Response(status_code=200)


@router.get("/all-data", tags=["spreadsheet"])
def fetch_access_and_refresh_tokens_for_login():
    return fetch_all_db_data()

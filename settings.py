from pydantic import BaseSettings


class Settings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uris: list[str]
    private_key_path: str
    jwt_expire_time: int
    user_sheet_id: str

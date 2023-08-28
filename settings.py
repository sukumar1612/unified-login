from pydantic import BaseSettings


class Settings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uris: list[str]

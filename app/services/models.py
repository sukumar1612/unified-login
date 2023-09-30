import pydantic


class User(pydantic.BaseModel):
    id: str  # email
    permission: str

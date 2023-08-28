import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.container import AppContainer
from app.routers import google_sso, sample_button
import app.services.router_dependencies

main_app = FastAPI()
main_app.add_middleware(
    SessionMiddleware,
    secret_key="YOUR_SECRET_KEY",
    same_site="lax",
    https_only=True,
)

container = AppContainer()
container.init_resources()
container.wire(modules=[__name__, app.services.router_dependencies])

main_app.include_router(google_sso.router)
main_app.include_router(sample_button.router)

if __name__ == '__main__':
    uvicorn.run(main_app, port=3000)

# oauth2.0 specs
# /authorize
# /token
# /introspect
# /revoke
# /userinfo

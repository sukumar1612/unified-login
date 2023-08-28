import os
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/button")
BASE_PATH = Path(os.path.abspath(__file__)).parent.parent
print(BASE_PATH)
TEMPLATE_FOLDER_PATH = os.path.join(BASE_PATH, "templates")
templates = Jinja2Templates(directory=TEMPLATE_FOLDER_PATH)


@router.get("/sample-google-sso", tags=["sample_templates"])
def sample_sso_button(request: Request):
    return templates.TemplateResponse("sample_template.html", {"request": request})

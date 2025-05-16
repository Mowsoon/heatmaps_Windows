from fastapi import APIRouter, Request
from config import templates
from helpers.html_handler import find_language
router = APIRouter(
    tags = ["Home"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def root(request: Request):
    languages, translation = find_language("home", request)
    return templates.TemplateResponse(
        name    = "home.html",
        context = {
            "request": request,
            "current_language": languages,
            "translations": translation
        }
    )
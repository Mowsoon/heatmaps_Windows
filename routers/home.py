from fastapi import APIRouter, Request
from config import template
from helpers.html_handler import find_language
router = APIRouter(
    tags = ["Home"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def root(request: Request):
    lang, translations = find_language("home", request)

    return template.TemplateResponse(
        name="home.html",
        context={
            "request": request,
            "translations": translations,
            "current_lang": lang
        }
    )
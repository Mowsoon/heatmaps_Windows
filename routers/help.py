from fastapi import APIRouter, Request
from helpers.html_handler import find_language
from config import template

router = APIRouter(
    prefix="/help",
    tags=["help"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def help(request: Request):
    """
    Serves the documentation page (help.html).
    """
    lang, translations = find_language("help", request)

    return template.TemplateResponse(
        name="help.html",
        context={
            "request": request,
            "translations": translations,
            "current_lang": lang
        }
    )
from fastapi import APIRouter, Request
from config import template
from helpers.html_handler import find_language, list_data

router = APIRouter(
    prefix="/maps",
    tags=["maps"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def maps(request: Request):
    lang, translations = find_language("maps", request)
    return template.TemplateResponse(
        name="maps.html", 
        context={
            "request": request,
            "translations": translations,
            "current_lang": lang,
            "maps": list_data()
        }
    )
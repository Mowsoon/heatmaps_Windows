from fastapi import APIRouter, Request, HTTPException
from helpers.html_handler import find_language
from config import template

router = APIRouter(
    prefix="/help",
    tags=["help"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def help(request: Request):
    lang, translations = find_language("help", request)
    return template.TemplateResponse(
        name="help.html", 
        context={
                "request": request,
                "translations": translations,
                "current_lang": lang
        }
    )
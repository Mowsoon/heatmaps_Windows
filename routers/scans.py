from fastapi import APIRouter, Request, File, UploadFile
from config import template
from helpers.html_handler import generate_preview, find_language
from helpers.file_handler import load_file


router = APIRouter(
    prefix="/scans",
    tags=["scans"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def scans(request: Request):
    lang, translations = find_language("scans", request)
    return template.TemplateResponse(
        name="scans.html", 
        context={
            "request": request,
            "maps": generate_preview(),
            "translations": translations,
            "current_lang": lang
        }
    )

@router.post("/")
async def upload_map(file: UploadFile = File(...)):
    return load_file("/scans", file)
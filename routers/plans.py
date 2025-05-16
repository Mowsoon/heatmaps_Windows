from fastapi import APIRouter, Request, File, UploadFile
from config import template, MAPS_DIR
from helpers.html_handler import generate_preview, find_language
from helpers.file_handler import load_file, delete_file

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def plans(request: Request):
    lang, translations = find_language("plans", request)

    return template.TemplateResponse(
        name="plans.html",
        context={
            "request": request,
            "maps": generate_preview(),
            "translations": translations,
            "current_lang": lang
        }
    )


@router.post("/")
async def upload_map(file: UploadFile = File(...)):
    return load_file("/plans", file)


@router.delete("/{map_name}")
async def delete_map(map_name: str):
    return delete_file(map_name)


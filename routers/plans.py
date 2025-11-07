from fastapi import APIRouter, Request, File, UploadFile
from config import template
from helpers.html_handler import generate_preview, find_language
from helpers.file_handler import load_file, delete_file

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def plans(request: Request):
    """
    Serves the 'Plans' page (plans.html).
    This page shows existing map previews and allows uploading new ones.
    """
    # Get language and translation dictionary
    lang, translations = find_language("plans", request)

    return template.TemplateResponse(
        name="plans.html",
        context={
            "request": request,
            "maps": generate_preview(),  # Get list of all map images
            "translations": translations,
            "current_lang": lang
        }
    )


@router.post("/")
async def upload_map(file: UploadFile = File(...)):
    """
    Endpoint for uploading a new map file (PNG, JPG, PDF).
    Called by the form on the 'Plans' page.
    """
    # Delegate file handling logic to the helper
    # Redirects back to /plans on success or failure
    return load_file("/plans", file)


@router.delete("/{map_name}")
async def delete_map(map_name: str):
    """
    Endpoint to delete a map image and its associated scan data.
    Called by the trash can icon on the 'Plans' page.
    """
    # Delegate deletion logic to the helper
    return delete_file(map_name)
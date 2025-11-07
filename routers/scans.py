from fastapi import APIRouter, Request, File, UploadFile, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from config import template, ClickPosition
from helpers.html_handler import generate_preview, find_language
from helpers.file_handler import load_file, find_map_url
from helpers.data_handler import delete_json, update_json_with_scan

router = APIRouter(
    prefix="/scans",
    tags=["scans"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def scans(request: Request):
    """
    Serves the 'Scans' page (scans.html).
    This page shows maps and allows starting a scan or uploading/downloading scan data.
    """
    lang, translations = find_language("scans", request)
    return template.TemplateResponse(
        name="scans.html",
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
    Called by the form on the 'Scans' page.
    """
    # Delegate file handling logic to the helper
    # Redirects back to /scans on success or failure
    return load_file("/scans", file)


@router.get("/{map_name}", response_class=HTMLResponse)
async def load_scan(map_name: str, request: Request):
    """
    Serves the individual scan page (scan_map.html) for a specific map.
    This is where the user clicks to perform scans.
    It deletes any previous (stale) JSON data for this map.
    """
    # Clear out old scan data before starting a new session
    delete_json(map_name)

    lang, translations = find_language("scan_map", request)
    map_url = find_map_url(map_name)  # Find the /static/maps/... URL

    if map_url:
        return template.TemplateResponse("scan_map.html", {
            "request": request,
            "map_name": map_name,
            "map_url": map_url,
            "translations": translations,
            "current_lang": lang
        })
    # If no map image is found, raise 404
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")


@router.post("/{map_name}")
async def update_scan(map_name: str, position: ClickPosition):
    """
    Endpoint called when the user clicks on the map in scan_map.html.
    It receives the (x, y) coordinates, performs a Wi-Fi scan,
    and saves the data to the JSON files.
    """
    # Delegate the core scanning and data saving logic to the helper
    update_json_with_scan(map_name, position.x, position.y)

    return JSONResponse(
        content={"status": "success", "message": f"Added scan for {map_name} at ({position.x}, {position.y})"})
from fastapi import APIRouter, Request, File, UploadFile, HTTPException
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


@router.get("/{map_name}", response_class=HTMLResponse)
async def load_scan(map_name: str, request: Request):
    delete_json(map_name)
    lang, translations = find_language("scan_map", request)
    map_url = find_map_url(map_name)
    if map_url:
        return template.TemplateResponse("scan_map.html", {
            "request": request,
            "map_name": map_name,
            "map_url": map_url,
            "translations": translations,
            "current_lang": lang
        })
    raise HTTPException(status_code=404, detail="Map not found")


@router.post("/{map_name}")
async def update_scan(map_name: str, position: ClickPosition):
    update_json_with_scan(map_name, position.x, position.y)
    return JSONResponse(
        content={"status": "success", "message": f"Added scan for {map_name} at ({position.x}, {position.y})"})
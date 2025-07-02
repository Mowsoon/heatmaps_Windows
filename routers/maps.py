from fastapi import APIRouter, Request, status, HTTPException
from config import template
from helpers.html_handler import find_language, list_data
from helpers.file_handler import find_map_url, find_map
from helpers.data_handler import find_ssid_list, find_data_list, find_channel_list
from helpers.heatmap_handler import draw_heatmap, channel_heatmap
from urllib.parse import unquote

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
@router.get("/{map_name}")
async def heatmaps(map_name: str, request: Request):
    lang, translations  = find_language("heatmap", request)
    map_url             = find_map_url(map_name)
    ssid_band_list      = find_ssid_list(map_name)
    channel_list        = find_channel_list(map_name)
    if map_url:
        if ssid_band_list:
            return template.TemplateResponse("heatmap.html", {
            "request": request,
            "map_name": map_name,
            "map_url": map_url,
            "translations": translations,
            "current_lang": lang,
            "ssid_band_list": ssid_band_list,
            "channel_list": channel_list
        })
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

@router.get("/{map_name}/signal/{ssid_band_key:path}")
async def display(map_name: str, ssid_band_key: str):
    map_name = unquote(map_name)
    ssid_band_key = unquote(ssid_band_key)
    data = find_data_list(map_name, ssid_band_key, "signal")
    map_info = find_map(map_name)
    if not map_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    return draw_heatmap(data, map_info)

@router.get("/{map_name}/channel/{channel}")
async def display(map_name: str, channel: str):
    map_name = unquote(map_name)
    channel = unquote(channel)
    data = find_data_list(map_name, channel, "channel")
    map_info = find_map(map_name)
    if not map_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")
    return channel_heatmap(data, map_info)
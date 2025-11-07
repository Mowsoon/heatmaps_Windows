# File: mowsoon/heatmaps_windows/heatmaps_Windows-d6faa9591d82b18e4be7509a6c9bc2161c9a7e6d/routers/maps.py

from fastapi import APIRouter, Request, status, HTTPException
from config import template
from helpers.html_handler import find_language, list_map
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
    """
    Serves the main 'Maps' page (maps.html).
    This page lists all maps that have existing scan data.
    """
    lang, translations = find_language("maps", request)
    return template.TemplateResponse(
        name="maps.html",
        context={
            "request": request,
            "translations": translations,
            "current_lang": lang,
            "maps": list_map()  # Get list of maps *with data*
        }
    )


@router.get("/{map_name}")
async def heatmaps(map_name: str, request: Request):
    """
    Serves the main visualization page (heatmap.html) for a specific map.
    This page shows the map and the checklist of SSIDs/Channels.
    """
    lang, translations = find_language("heatmap", request)
    map_url = find_map_url(map_name)
    ssid_band_list = find_ssid_list(map_name)
    channel_list = find_channel_list(map_name)

    if map_url:
        # Check if there is any data to visualize
        # (This check was corrected to handle cases where only channel data exists)
        if ssid_band_list or channel_list:
            return template.TemplateResponse("heatmap.html", {
                "request": request,
                "map_name": map_name,
                "map_url": map_url,
                "translations": translations,
                "current_lang": lang,
                "ssid_band_list": ssid_band_list,  # Used by JS checklist
                "channel_list": channel_list  # Used by JS checklist
            })
        # If no scan data exists for this map, raise 404
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    # If no map image file exists, raise 404
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")


@router.get("/{map_name}/signal/{ssid_band_key:path}")
async def display(map_name: str, ssid_band_key: str):
    """
    API endpoint that generates and returns a signal heatmap image.
    Called by JavaScript when a user selects an SSID from the checklist.

    :param map_name: The name of the map (e.g., "my_plan")
    :param ssid_band_key: The selected key (e.g., "MySSID [5GHz]")
    """
    # Decode URL-encoded characters (e.g., spaces, brackets)
    map_name = unquote(map_name)
    ssid_band_key = unquote(ssid_band_key)

    # 1. Find the raw data points for this key
    data = find_data_list(map_name, ssid_band_key, "signal")
    # 2. Find the file path for the base map image
    map_info = find_map(map_name)

    if not map_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    # 3. Generate the heatmap image and return it
    return draw_heatmap(data, map_info)


@router.get("/{map_name}/channel/{channel}")
async def display(map_name: str, channel: str):
    """
    API endpoint that generates and returns a channel congestion heatmap image.
    Called by JavaScript when a user selects a Channel from the checklist.

    :param map_name: The name of the map (e.g., "my_plan")
    :param channel: The selected key (e.g., "Channel_6")
    """
    # Decode URL-encoded characters
    map_name = unquote(map_name)
    channel = unquote(channel)

    # 1. Find the raw data points for this channel
    data = find_data_list(map_name, channel, "channel")
    # 2. Find the file path for the base map image
    map_info = find_map(map_name)

    if not map_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Map not found")

    # 3. Generate the channel heatmap image and return it
    return channel_heatmap(data, map_info)
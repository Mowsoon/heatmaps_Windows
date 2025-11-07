from fastapi import APIRouter, File, UploadFile
from helpers.data_handler import load_data, send_data


router = APIRouter(
    tags=["data"],
    responses={404: {"description": "Not found"}},
)

@router.post("/load/{map_name}")
async def upload_data(map_name: str, file: UploadFile = File(...)):
    """
    Endpoint to upload a previously saved .json scan file.
    Called by the "Load" button on the 'scans' page.
    """
    return load_data(map_name, file)


@router.get("/save/{map_name}")
async def save_data(map_name: str):
    """
    Endpoint to download the current .json scan data.
    Called by the "Save" button on the 'scans' page.
    """
    return send_data(map_name)
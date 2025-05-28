from fastapi import File, UploadFile, status, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from pathlib import Path
from config import DATA_DIR, MAPS_DIR, MAPS_ALLOWED_EXTENSIONS
from datetime import datetime

def list_data():
    data = []
    for file in DATA_DIR.iterdir():
        if file.suffix.lower() == ".json":
            for ext in MAPS_ALLOWED_EXTENSIONS:
                corresponding_map = MAPS_DIR / (file.stem + ext)
                if corresponding_map.exists():
                    data.append({"name": file.stem})
                    break 
    return data

def load_data(map_name: str, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()

    if ext != ".json":
        return RedirectResponse(url="/scans", status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_path = DATA_DIR / f"{map_name}.json"
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return RedirectResponse(url="/scans", status_code=status.HTTP_303_SEE_OTHER)


def send_data(map_name: str):
    file_path = DATA_DIR / f"{map_name}.json"
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=f"{map_name}.json",
        media_type='application/json',
        headers={"Content-Disposition": f"attachment; filename={map_name}.json"}
    )
    
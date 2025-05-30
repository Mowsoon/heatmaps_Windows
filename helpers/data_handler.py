from fastapi import File, UploadFile, status, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from pathlib import Path
from config import DATA_DIR
import json
from helpers.scan import extract_ssid



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

def update_json_with_scan(map_name: str):
    file_path = DATA_DIR / f"{map_name}.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    results = extract_ssid()

    for network in results:
        ssid    = network["ssid"]
        band    = network["band"]
        bssid   = network["bssid"]
        signal  = network["signal"]

        key = f"{ssid} [{band}]"
        if key not in data:
            data[key] = []

        data[key].append({
            "bssid": bssid,
            "signal": signal
        })

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return {"status": "success", "message": f"Scan data saved to {file_path.name}"}
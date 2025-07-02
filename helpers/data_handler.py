from fastapi import File, UploadFile, status, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from pathlib import Path
from config import SIGNAL_DIR, CHANNEL_DIR
import json
from helpers.scan_handler import extract_scan



def load_data(map_name: str, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()

    if ext != ".json":
        return RedirectResponse(url="/scans", status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_path = SIGNAL_DIR / f"{map_name}.json"
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return RedirectResponse(url="/scans", status_code=status.HTTP_303_SEE_OTHER)


def send_data(map_name: str):
    file_path = SIGNAL_DIR / f"{map_name}.json"
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=f"{map_name}.json",
        media_type='application/json',
        headers={"Content-Disposition": f"attachment; filename={map_name}.json"}
    )

def extract_signal(results, x, y, map_name):
    file_path = SIGNAL_DIR / f"{map_name}.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

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
            "signal": signal,
            "x": x,
            "y": y
        })
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return f"Scan data saved to {file_path.name}"

def extract_channel(channels: dict[int, int], x: int, y: int, map_name: str):
    file_path = CHANNEL_DIR / f"{map_name}.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}

    key = f"{x},{y}"

    data[key] = {f"channel{chan}": count for chan, count in channels.items()}

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return f"Scan data saved to {file_path.name}"

def update_json_with_scan(map_name: str, x: int, y: int):
    results, channels   = extract_scan()
    signal_mess         = extract_signal(results, x, y, map_name)
    channel_mess        = extract_channel(channels, x, y, map_name)

    return {"status": "success", "message": signal_mess + "\n" + channel_mess}



def delete_signal(map_name: str):
    file_path = SIGNAL_DIR / f"{map_name}.json"
    if file_path.exists():
        file_path.unlink()
        return f"{file_path.name} has been deleted"
    else:
        return f"{file_path.name} does not exist"

def delete_channel(map_name: str):
    file_path = CHANNEL_DIR / f"{map_name}.json"
    if file_path.exists():
        file_path.unlink()
        return f"{file_path.name} has been deleted"
    else:
        return f"{file_path.name} does not exist"

def delete_json(map_name: str):
    signal_mess     = delete_signal(map_name)
    channel_mess    = delete_channel(map_name)
    return {"status": "deleted", "message": signal_mess + "\n" + channel_mess}

def find_ssid_list(map_name: str):
    json_path = SIGNAL_DIR / f"{map_name}.json"
    if not json_path.exists():
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.keys())

def find_data_list(map_name: str, ssid_band_key: str):
    json_path = SIGNAL_DIR / f"{map_name}.json"
    if not json_path.exists():
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(ssid_band_key, [])
    except Exception as e:
        return []
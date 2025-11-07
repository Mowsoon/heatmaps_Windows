from typing import Any, Dict, List, Union
from fastapi import File, UploadFile, status, HTTPException
from fastapi.responses import RedirectResponse, FileResponse
from pathlib import Path
from config import SIGNAL_DIR, CHANNEL_DIR
import json
from helpers.scan_handler import extract_scan


def load_data(map_name: str, file: UploadFile = File(...)) -> RedirectResponse:
    """
    Handles uploading a .json scan file for a specific map.
    This is used for the "Load" functionality on the scans page.
    """
    ext = Path(file.filename).suffix.lower()

    if ext != ".json":
        # If the file is not a JSON, redirect with an error
        return RedirectResponse(url="/scans", status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # Define the target file path in the signal directory
    file_path = SIGNAL_DIR / f"{map_name}.json"

    # Write the uploaded file's content to the target file
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
        # Redirect on failure
        return RedirectResponse(url="/scans", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Redirect back to the scans page on success
    return RedirectResponse(url="/scans", status_code=status.HTTP_303_SEE_OTHER)


def send_data(map_name: str) -> FileResponse:
    """
    Handles downloading a .json scan file for a specific map.
    This is used for the "Save" functionality on the scans page.
    """
    file_path = SIGNAL_DIR / f"{map_name}.json"

    if not file_path.exists():
        # If the file doesn't exist, raise a 404 error
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Return the file as a downloadable attachment
    return FileResponse(
        path=file_path,
        filename=f"{map_name}.json",
        media_type='application/json',
        headers={"Content-Disposition": f"attachment; filename={map_name}.json"}
    )


def extract_signal(results: List[Dict[str, Union[str, float]]], x: int, y: int, map_name: str) -> str:
    """
    Takes a list of network scan results and appends them to this map's signal JSON file.
    Organizes data by SSID and Band.
    """
    file_path = SIGNAL_DIR / f"{map_name}.json"

    # Load existing data from the file, or start with an empty dict
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data: Dict[str, List] = json.load(f)
        except json.JSONDecodeError:
            data = {}  # Overwrite corrupted file
    else:
        data = {}

    # Process each network found in the scan result
    for network in results:
        ssid = str(network["ssid"])
        band = str(network["band"])
        bssid = str(network["bssid"])
        signal = float(network["signal"])

        # Create a unique key for the SSID + Band combination
        key = f"{ssid} [{band}]"

        if key not in data:
            data[key] = []

        # Append the new scan point data
        data[key].append({
            "bssid": bssid,
            "signal": signal,
            "x": x,
            "y": y
        })

    # Write the updated data back to the JSON file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return f"Scan data saved to {file_path.name}"
    except Exception as e:
        return f"Error saving signal data: {e}"


def extract_channel(channels: Dict[int, int], x: int, y: int, map_name: str) -> str:
    """
    Takes a dictionary of channel counts and appends them to this map's channel JSON file.
    Organizes data by channel number.
    """
    file_path = CHANNEL_DIR / f"{map_name}.json"

    # Load existing data from the file, or start with an empty dict
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data: Dict[str, List] = json.load(f)
        except json.JSONDecodeError:
            data = {}  # Overwrite corrupted file
    else:
        data = {}

    # Process each channel count
    for channel, count in channels.items():
        key = f"Channel_{channel}"  # e.g., "Channel_6"

        if key not in data:
            data[key] = []

        # Append the new scan point data
        data[key].append({
            "x": x,
            "y": y,
            "count": count
        })

    # Write the updated data back to the JSON file
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return f"Channel data saved to {file_path.name}"
    except Exception as e:
        return f"Error saving channel data: {e}"


def update_json_with_scan(map_name: str, x: int, y: int) -> Dict[str, str]:
    """
    Main function called by the API when a user clicks on the scan map.
    It performs a scan and updates both signal and channel JSON files.
    """
    # 1. Perform the OS-specific scan
    results, channels = extract_scan()

    # 2. Save the signal (SSID) results
    signal_mess = extract_signal(results, x, y, map_name)

    # 3. Save the channel count results
    channel_mess = extract_channel(channels, x, y, map_name)

    return {"status": "success", "message": signal_mess + "\n" + channel_mess}


def delete_signal(map_name: str) -> str:
    """Utility function to delete the signal JSON file for a map."""
    file_path = SIGNAL_DIR / f"{map_name}.json"
    if file_path.exists():
        try:
            file_path.unlink()
            return f"{file_path.name} has been deleted"
        except Exception as e:
            return f"Error deleting {file_path.name}: {e}"
    else:
        return f"{file_path.name} does not exist"


def delete_channel(map_name: str) -> str:
    """Utility function to delete the channel JSON file for a map."""
    file_path = CHANNEL_DIR / f"{map_name}.json"
    if file_path.exists():
        try:
            file_path.unlink()
            return f"{file_path.name} has been deleted"
        except Exception as e:
            return f"Error deleting {file_path.name}: {e}"
    else:
        return f"{file_path.name} does not exist"


def delete_json(map_name: str) -> Dict[str, str]:
    """
    Deletes both signal and channel JSON files for a map.
    Called when starting a new scan or deleting a map.
    """
    signal_mess = delete_signal(map_name)
    channel_mess = delete_channel(map_name)
    return {"status": "deleted", "message": signal_mess + "\n" + channel_mess}


def find_ssid_list(map_name: str) -> List[str]:
    """
    Finds the list of all "SSID [Band]" keys from a map's signal JSON file.
    Used to populate the checklist on the heatmap visualization page.
    """
    json_path = SIGNAL_DIR / f"{map_name}.json"
    if not json_path.exists():
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        return list(data.keys())
    except Exception:
        return []  # Return empty list on file error


def find_channel_list(map_name: str) -> List[str]:
    """
    Finds the list of all "Channel_X" keys from a map's channel JSON file.
    Used to populate the checklist on the heatmap visualization page.
    """
    json_path = CHANNEL_DIR / f"{map_name}.json"
    if not json_path.exists():
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        return list(data.keys())
    except Exception:
        return []  # Return empty list on file error


def find_data_list(map_name: str, key: str, data_type: str) -> List[Dict[str, Any]]:
    """
    Retrieves the raw list of data points (x, y, signal/count) for a
    specific key (e.g., "MySSID [5GHz]" or "Channel_6") from the correct JSON file.
    """
    if data_type == "channel":
        json_path = CHANNEL_DIR / f"{map_name}.json"
    else:  # Default to signal
        json_path = SIGNAL_DIR / f"{map_name}.json"

    if not json_path.exists():
        return []

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data: Dict[str, List[Dict[str, Any]]] = json.load(f)
        # Return the list of data points for the requested key, or empty list
        return data.get(key, [])
    except Exception:
        return []
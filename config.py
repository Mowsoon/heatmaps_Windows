# File: mowsoon/heatmaps_windows/heatmaps_Windows-d6faa9591d82b18e4be7509a6c9bc2161c9a7e6d/config.py

from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel
import sys
import pywifi
import subprocess
from typing import Optional

# Initialize Jinja2 for HTML templates
template = Jinja2Templates(directory="templates")

# --- Path Configuration ---
# Determine the base directory of the application
# This is crucial for when the app is frozen into an executable
if getattr(sys, 'frozen', False):
    # Running as a compiled executable (e.g., via Nuitka)
    BASE_DIR = Path(sys.executable).parent
else:
    # Running as a standard Python script
    BASE_DIR = Path(__file__).parent


# Define allowed file extensions for map uploads
MAPS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf"]
# Define extensions that are checked for existing maps
MAPS_POSSIBLE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

# Define all primary directories
MAPS_DIR = BASE_DIR / "static/maps"
SIGNAL_DIR = BASE_DIR / "static/data/signal"
DATA_DIR = BASE_DIR / "static/data"
CHANNEL_DIR = BASE_DIR / "static/data/channel"
LANG_DIR = BASE_DIR / "languages"
GENERATED_DIR = BASE_DIR / "static/generated"

# Ensure all data directories exist on startup
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
for path in [MAPS_DIR, SIGNAL_DIR, CHANNEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# --- Pydantic Model ---

class ClickPosition(BaseModel):
    """
    Pydantic model to validate the (x, y) coordinates
    sent from the JavaScript fetch request.
    """
    x: int
    y: int

# --- OS-Specific Wi-Fi Interface Configuration ---

def get_wifi_interface_linux() -> Optional[str]:
    """
    Finds the name of the first wireless interface on Linux using 'iw dev'.
    """
    try:
        # Run 'iw dev' command
        output = subprocess.check_output(["iw", "dev"], encoding="utf-8")
        # Parse output to find the interface name
        for line in output.splitlines():
            if line.strip().startswith("Interface"):
                return line.split()[1]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return None


# Determine the operating system and find the Wi-Fi interface
if sys.platform.startswith("win"):
    SYS = "Windows"
    try:
        # On Windows, use pywifi to get the interface
        WIFI_INTERFACE = pywifi.PyWiFi().interfaces()[0]
    except Exception:
        WIFI_INTERFACE = None
elif sys.platform.startswith("linux"):
    SYS = "Linux"
    # On Linux, use our helper function
    WIFI_INTERFACE = get_wifi_interface_linux()
else:
    SYS = "Unknown"
    WIFI_INTERFACE = None
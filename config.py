from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel
import sys
import pywifi
import subprocess

template = Jinja2Templates(directory="templates")

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent


MAPS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf"]
MAPS_POSSIBLE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

MAPS_DIR = BASE_DIR / "static/maps"
SIGNAL_DIR = BASE_DIR / "static/data/signal"
CHANNEL_DIR = BASE_DIR / "static/data/channel"
LANG_DIR = BASE_DIR / "languages"
GENERATED_DIR = BASE_DIR / "static/generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

class ClickPosition(BaseModel):
    x: int
    y: int

def get_wifi_interface_linux() -> str | None:
    try:
        output = subprocess.check_output(["iw", "dev"], encoding="utf-8")
        for line in output.splitlines():
            if line.strip().startswith("Interface"):
                return line.split()[1]
    except subprocess.CalledProcessError:
        return None


if sys.platform.startswith("win"):
    SYS = "Windows"
    WIFI_INTERFACE = pywifi.PyWiFi().interfaces()[0]

elif sys.platform.startswith("linux"):
    SYS = "Linux"
    WIFI_INTERFACE = get_wifi_interface_linux
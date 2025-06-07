from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel
import sys

template = Jinja2Templates(directory="templates")

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

MAPS_DIR = BASE_DIR / "static/maps"
MAPS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf"]
MAPS_POSSIBLE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

DATA_DIR = BASE_DIR / "static/data"

class ClickPosition(BaseModel):
    x: int
    y: int
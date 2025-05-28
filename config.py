from fastapi.templating import Jinja2Templates
from pathlib import Path

template = Jinja2Templates(directory="templates")


MAPS_DIR = Path("static/maps")
MAPS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf"]
MAPS_POSSIBLE_EXTENSIONS = [".png", ".jpg", ".jpeg"]

DATA_DIR = Path("static/data")


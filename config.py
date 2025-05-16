from fastapi.templating import Jinja2Templates
from pathlib import Path

template = Jinja2Templates(directory="templates")


MAPS_DIR = Path("static/maps")
PREVIEWS_DIR = MAPS_DIR / "previews"
MAPS_ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".pdf"]

DATA_DIR = Path("static/data")


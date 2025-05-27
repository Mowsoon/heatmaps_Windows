from fastapi import Request
from pathlib import Path
from config import MAPS_DIR
import json

def find_language(html_page_name: str,request: Request):
    language = request.cookies.get('lang', 'en')
    if language not in ["en", "fr"]:
        language = "en"
    language_path = Path(f"languages/{language}/{html_page_name}.json")


    if not language_path.exists():
        language_path = Path(f"languages/en/{html_page_name}.json")

    with open(language_path, "r", encoding="utf-8") as f:
        translation = json.load(f)

    return language, translation



def generate_preview():
    maps = []
    for file in MAPS_DIR.iterdir():
        if file.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            maps.append({
                "name": file.stem,
                "preview_url": f"/static/maps/{file.name}"
            })
    return maps
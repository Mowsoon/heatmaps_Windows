from typing import Dict, List, Tuple
from fastapi import Request
from config import MAPS_DIR, MAPS_ALLOWED_EXTENSIONS, MAPS_POSSIBLE_EXTENSIONS, SIGNAL_DIR, LANG_DIR
import json


def find_language(html_page_name: str, request: Request) -> Tuple[str, Dict]:
    language = request.cookies.get('lang', 'en')
    if language not in ["en", "fr"]:
        language = "en"
    language_path = LANG_DIR / language / f"{html_page_name}.json"

    if not language_path.exists():
        language_path = LANG_DIR / "en" / f"{html_page_name}.json"

    with open(language_path, "r", encoding="utf-8") as f:
        translation = json.load(f)

    return language, translation


def generate_preview() -> List[Dict[str, str]]:
    maps = []
    for file in MAPS_DIR.iterdir():
        if file.suffix.lower() in MAPS_POSSIBLE_EXTENSIONS:
            maps.append({
                "name": file.stem,
                "preview_url": f"/static/maps/{file.name}"
            })
    return maps


def list_map() -> List[Dict[str, str]]:
    data = []
    for file in SIGNAL_DIR.iterdir():
        if file.suffix.lower() == ".json":
            for ext in MAPS_POSSIBLE_EXTENSIONS:
                corresponding_map = MAPS_DIR / (file.stem + ext)
                if corresponding_map.exists():
                    data.append({"name": file.stem})
                    break
    return data

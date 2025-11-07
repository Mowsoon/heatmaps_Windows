from typing import Dict, List, Tuple, Any
from fastapi import Request
from config import MAPS_DIR, MAPS_POSSIBLE_EXTENSIONS, SIGNAL_DIR, LANG_DIR
import json


def find_language(html_page_name: str, request: Request) -> Tuple[str, Dict[str, Any]]:
    """
    Determines the correct language and loads the corresponding translation JSON.
    - Reads language from the 'lang' cookie (defaults to 'en').
    - Loads the JSON file (e.g., "languages/fr/home.json").
    - Falls back to English if a translation file is missing.
    """
    # 1. Get language from cookie, default to 'en'
    language = request.cookies.get('lang', 'en')
    if language not in ["en", "fr"]:
        language = "en"

    # 2. Construct the path to the translation file
    language_path = LANG_DIR / language / f"{html_page_name}.json"

    # 3. Fallback to English if the specific language file doesn't exist
    if not language_path.exists():
        language = "en"  # Explicitly set lang back to 'en' for context
        language_path = LANG_DIR / "en" / f"{html_page_name}.json"

    # 4. Load the JSON content
    try:
        with open(language_path, "r", encoding="utf-8") as f:
            translation = json.load(f)
    except Exception as e:
        print(f"Error loading translation file {language_path}: {e}")
        translation = {}

    return language, translation


def generate_preview() -> List[Dict[str, str]]:
    """
    Scans the /static/maps directory and builds a list of all available maps.
    Used to display maps on the 'plans' and 'scans' pages.
    """
    maps = []
    for file in MAPS_DIR.iterdir():
        # Check if the file has one of the allowed image extensions
        if file.suffix.lower() in MAPS_POSSIBLE_EXTENSIONS:
            maps.append({
                "name": file.stem,  # File name without extension (e.g., "my_plan")
                "preview_url": f"/static/maps/{file.name}"
            })
    return maps


def list_map() -> List[Dict[str, str]]:
    """
    Scans the /static/data/signal directory to find which maps have scan data.
    Used to display maps on the 'maps' (visualization) page.

    This ensures that the visualization page only lists maps that actually
    have scan data to be viewed.
    """
    data = []
    # 1. Iterate over all JSON files in the signal data directory
    for file in SIGNAL_DIR.iterdir():
        if file.suffix.lower() == ".json":
            # 2. For each scan file, check if a corresponding map image still exists
            for ext in MAPS_POSSIBLE_EXTENSIONS:
                corresponding_map = MAPS_DIR / (file.stem + ext)
                if corresponding_map.exists():
                    # 3. If both scan data and map image exist, add it to the list
                    data.append({"name": file.stem})
                    # Found a match, no need to check other extensions for this file
                    break
    return data
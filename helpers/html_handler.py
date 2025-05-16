from fastapi import Request
from pathlib import Path
import json

def find_language(html_page_name: str,request: Request):
    language = request.cookies.get('language', 'en')
    language_path = Path(f"languages/{language}/{html_page_name}.json")

    if not language_path.exists():
        language_path = Path(f"languages/en/{html_page_name}.json")

    with open(language_path, "r") as f:
        translation = json.load(f)

    return language, translation
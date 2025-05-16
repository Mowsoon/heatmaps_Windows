from fastapi import Request
from pathlib import Path
from config import MAPS_DIR, PREVIEWS_DIR
from pdf2image import convert_from_path
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


def generate_preview_for_pdf(pdf_path: Path, preview_path: Path):
    images = convert_from_path(str(pdf_path),first_page=1, last_page=1)
    if images:
        image = images[0]
        if image.height > image.width:
            image = image.rotate(90, expand=True)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(str(preview_path), "PNG")


def generate_preview():
    maps = []
    for file in MAPS_DIR.iterdir():
        if file.suffix.lower() in [".png", ".jpg", ".jpeg", ".pdf"]:
            name = file.stem
            if file.suffix.lower() == ".pdf":
                preview_file = PREVIEWS_DIR / f"{name}.png"
                if not preview_file.exists():
                    generate_preview_for_pdf(file, preview_file)
                preview_url = f"/static/maps/previews/{preview_file.name}"
            else:
                preview_url = f"/static/maps/{file.name}"
            maps.append({
                "name": name,
                "preview_url": preview_url
            })
    return maps
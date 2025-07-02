from fastapi import File, UploadFile, status
from fastapi.responses import RedirectResponse, JSONResponse
from config import MAPS_DIR, MAPS_ALLOWED_EXTENSIONS
from pathlib import Path
from pdf2image import convert_from_bytes
from helpers.data_handler import delete_json


def load_file(page_path: str, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()

    if ext not in MAPS_ALLOWED_EXTENSIONS:
        return RedirectResponse(url=page_path, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_path = MAPS_DIR / file.filename
    if file_path.exists():
        return RedirectResponse(url=page_path, status_code=status.HTTP_409_CONFLICT)

    if ext == ".pdf":
        name = Path(file.filename).stem
        file_path = MAPS_DIR / f"{name}.png"
        if file_path.exists():
            return RedirectResponse(url=page_path, status_code=status.HTTP_409_CONFLICT)

        pdf_bytes = file.file.read()
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)
        if images:
            image = images[0]
            if image.height > image.width:
                image = image.rotate(90, expand=True)
            MAPS_DIR.mkdir(parents=True, exist_ok=True)
            image.save(str(file_path), "PNG")
    else:
        MAPS_DIR.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

    return RedirectResponse(url=page_path, status_code=status.HTTP_303_SEE_OTHER)


def delete_file(map_name: str):
    for ext in [".png", ".jpg", ".jpeg"]:   
        map_file = MAPS_DIR / f"{map_name}{ext}"
        if map_file.exists():
            map_file.unlink()
        delete_json(map_name)

    return JSONResponse(content={"status": "deleted"}, status_code=status.HTTP_200_OK)


def find_map_url(map_name: str):
    for ext in [".png", ".jpg", ".jpeg"]:
        map_file = MAPS_DIR / f"{map_name}{ext}"
        if map_file.exists():
            return f"/static/maps/{map_name}{ext}"
    return None

def find_map(map_name: str):
    for ext in [".png", ".jpg", ".jpeg"]:
        filename = f"{map_name}{ext}"
        map_file = MAPS_DIR / filename
        if map_file.exists():
            return map_file
    return None
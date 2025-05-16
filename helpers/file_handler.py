from fastapi import File, UploadFile, status
from fastapi.responses import RedirectResponse, JSONResponse
from config import MAPS_DIR, PREVIEWS_DIR, MAPS_ALLOWED_EXTENSIONS
from pathlib import Path


def load_file(pagename: str, file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()

    if ext not in MAPS_ALLOWED_EXTENSIONS:
        return RedirectResponse(url=pagename, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_path = MAPS_DIR / file.filename
    if file_path.exists():
        return RedirectResponse(url=pagename, status_code=status.HTTP_409_CONFLICT)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return RedirectResponse(url=pagename, status_code=status.HTTP_303_SEE_OTHER)


def delete_file(map_name: str):
    for ext in [".png", ".jpg", ".jpeg", ".pdf"]:
        map_file = MAPS_DIR / f"{map_name}{ext}"
        if map_file.exists():
            map_file.unlink()

    preview_file = PREVIEWS_DIR / f"{map_name}.png"
    if preview_file.exists():
        preview_file.unlink()

    return JSONResponse(content={"status": "deleted"}, status_code=status.HTTP_200_OK)



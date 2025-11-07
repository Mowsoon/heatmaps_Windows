from fastapi import File, UploadFile, status
from fastapi.responses import RedirectResponse, JSONResponse
from config import MAPS_DIR, MAPS_ALLOWED_EXTENSIONS
from pathlib import Path
from pdf2image import convert_from_bytes
from helpers.data_handler import delete_json
from typing import Optional, Union


def load_file(page_path: str, file: UploadFile = File(...)) -> RedirectResponse:
    """
    Handles uploading a new map file (Image or PDF).
    It validates the file type, checks for conflicts, converts PDFs to PNGs,
    and saves the final image to the MAPS_DIR.
    """
    # Get the file extension (e.g., ".pdf", ".png")
    ext = Path(file.filename).suffix.lower()

    # Check if the extension is in the allowed list
    if ext not in MAPS_ALLOWED_EXTENSIONS:
        return RedirectResponse(url=page_path, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    file_path = MAPS_DIR / file.filename

    # Check if a file with the same name already exists
    if file_path.exists():
        return RedirectResponse(url=page_path, status_code=status.HTTP_409_CONFLICT)

    # Special handling for PDF files
    if ext == ".pdf":
        name = Path(file.filename).stem
        # Define the output path as .png
        file_path = MAPS_DIR / f"{name}.png"

        if file_path.exists():
            return RedirectResponse(url=page_path, status_code=status.HTTP_409_CONFLICT)

        # Read PDF bytes and convert the first page to an image
        pdf_bytes = file.file.read()
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1)

        if images:
            image = images[0]
            # Auto-rotate the image if it's in portrait mode (taller than wide)
            if image.height > image.width:
                image = image.rotate(90, expand=True)

            MAPS_DIR.mkdir(parents=True, exist_ok=True)
            # Save the converted image as PNG
            image.save(str(file_path), "PNG")
    else:
        # Standard image file (PNG, JPG, JPEG)
        MAPS_DIR.mkdir(parents=True, exist_ok=True)
        # Write the file bytes directly to the maps directory
        with open(file_path, "wb") as f:
            f.write(file.file.read())

    # Redirect the user back to the page they uploaded from
    return RedirectResponse(url=page_path, status_code=status.HTTP_303_SEE_OTHER)


def delete_file(map_name: str) -> JSONResponse:
    """
    Deletes a map image file and its associated JSON scan data.
    """
    # Iterate through possible image extensions to find the file
    for ext in [".png", ".jpg", ".jpeg"]:
        map_file = MAPS_DIR / f"{map_name}{ext}"
        if map_file.exists():
            map_file.unlink()  # Delete the image file

    # Call the function from data_handler to delete associated scan data
    delete_json(map_name)

    return JSONResponse(content={"status": "deleted"}, status_code=status.HTTP_200_OK)


def find_map_url(map_name: str) -> Optional[str]:
    """
    Finds the full, web-accessible URL for a given map name (without extension).
    Returns the URL (e.g., "/static/maps/my_map.png") or None if not found.
    """
    for ext in [".png", ".jpg", ".jpeg"]:
        map_file = MAPS_DIR / f"{map_name}{ext}"
        if map_file.exists():
            # Return the static URL
            return f"/static/maps/{map_name}{ext}"
    return None


def find_map(map_name: str) -> Optional[Path]:
    """
    Finds the full file system Path object for a given map name.
    Returns the Path object or None if not found.
    """
    for ext in [".png", ".jpg", ".jpeg"]:
        filename = f"{map_name}{ext}"
        map_file = MAPS_DIR / filename
        if map_file.exists():
            # Return the Pathlib Path object
            return map_file
    return None
# File: mowsoon/heatmaps_windows/heatmaps_Windows-d6faa9591d82b18e4be7509a6c9bc2161c9a7e6d/main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import home, plans, scans, maps, help, change_language, data
from config import BASE_DIR

# Initialize the FastAPI application
# We disable the default docs/redoc/openapi URLs for a cleaner public-facing app
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# --- Static Files ---
# Mount the 'static' directory to serve CSS, JS, images, and map data
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

# --- Routers ---
# Include all the router files to organize API endpoints
app.include_router(home.router)
app.include_router(plans.router)
app.include_router(scans.router)
app.include_router(maps.router)
app.include_router(help.router)
app.include_router(change_language.router)
app.include_router(data.router)


# --- Main Entry Point ---
if __name__ == "__main__":
    import uvicorn
    # Run the application using uvicorn
    # This block is only executed when running "python main.py"
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
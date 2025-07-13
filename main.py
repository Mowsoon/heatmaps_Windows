from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import home, plans, scans, maps, help, change_language, data
from config import BASE_DIR

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")
app.include_router(home.router)
app.include_router(plans.router)
app.include_router(scans.router)
app.include_router(maps.router)
app.include_router(help.router)
app.include_router(change_language.router)
app.include_router(data.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

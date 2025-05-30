from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import home, plans, scans, maps, change_language, data

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(home.router)
app.include_router(plans.router)
app.include_router(scans.router)
app.include_router(maps.router)
app.include_router(change_language.router)
app.include_router(data.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

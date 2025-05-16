from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import home, change_language

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(home.router)
app.include_router(change_language.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

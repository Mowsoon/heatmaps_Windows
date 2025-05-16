from fastapi import APIRouter, Request
from config import templates

router = APIRouter(
    tags = ["Home"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        name    = "home.html",
        context = {
            "request": request
        }
    )
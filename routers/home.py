from fastapi import APIRouter


router = APIRouter(
    tags = ["Home"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def root():
    return {"message": "Hello World"}
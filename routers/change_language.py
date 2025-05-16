from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse



router = APIRouter(
    prefix = "/change_language"
)

@router.get("/{language}")
async def change_language(language: str, request: Request):
    if language not in ['fr', 'en']:
        language = 'en'
    next_url = request.query_params.get("next", "/")
    redirect_response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="language", value=language)
    return redirect_response
from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse

router = APIRouter(prefix="/change_language")

@router.get("/{lang}")
async def change_language(lang: str, request: Request):
    if lang not in ['fr', 'en']:
        lang = 'en'
    next_url = request.query_params.get("next", "/")
    
    if urlparse(next_url).netloc:
        next_url = "/"
    
    redirect_response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="lang", value=lang)
    return redirect_response



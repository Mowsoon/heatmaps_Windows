from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/change_language")

@router.get("/{lang}")
async def change_language(lang: str, request: Request):
    if lang not in ['fr', 'en']:
        lang = 'en'
    next_url = request.query_params.get("next", "/")
    redirect_response = RedirectResponse(url=next_url, status_code = status.HTTP_303_SEE_OTHER)
    redirect_response.set_cookie(key="lang", value=lang)
    return redirect_response


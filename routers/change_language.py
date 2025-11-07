from fastapi import APIRouter, status, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse

router = APIRouter(prefix="/change_language")


@router.get("/{lang}")
async def change_language(lang: str, request: Request):
    """
    Endpoint to change the application's language.
    It sets a 'lang' cookie and redirects the user back to their
    previous page (passed as the 'next' query parameter).
    """
    if lang not in ['fr', 'en']:
        lang = 'en'  # Default to English if lang is invalid

    # Get the return URL from query params, default to home '/'
    next_url = request.query_params.get("next", "/")

    # Basic security check: prevent open redirect attacks
    # If a full domain (e.g., evil.com) is in 'next_url',
    # just redirect to the homepage.
    if urlparse(next_url).netloc:
        next_url = "/"

    # Create a redirect response
    redirect_response = RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)

    # Set the language cookie
    redirect_response.set_cookie(key="lang", value=lang)

    return redirect_response
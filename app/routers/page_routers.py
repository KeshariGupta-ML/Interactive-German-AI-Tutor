from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database.models import User
from sqlalchemy.orm import Session

from app.database.connection import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.get("/")
async def root_redirect(request: Request):
    """Checks if user token cookie exists. Redirects to chat or login."""
    token = request.cookies.get("access_token")
    if token:
        return RedirectResponse(url="/chat", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request})


# =====================================================================
# 4. DEFINE GLOBAL VIEW CONTROLLERS (Root Page Navigation)
# =====================================================================
@router.get("/chat")
async def get_chat_page(request: Request, db: Session = Depends(get_db)):
    """Renders the chat page only if the user is authenticated and has an API key configured."""
    templates = request.app.state.templates

    # 1. Identify the current logged-in user using their session cookie
    token = request.cookies.get("access_token")
    if not token or not token.startswith("session_"):
        # If no active session cookie exists, boot them out to log in
        return RedirectResponse(url="/login?error=unauthorized", status_code=303)

    # Extract the email string stored inside the cookie container
    user_email = token.replace("session_", "")

    # 2. Query the live database to check the user's profile record
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        return RedirectResponse(url="/login?error=unauthorized", status_code=303)

    # 3. Guard Gate: Verify if their workspace API key profile column is blank
    if not user.encrypted_gemini_key or user.encrypted_gemini_key.strip() == "":
        # Automatically redirect them to configure their credentials
        return RedirectResponse(url="/setup-key?error=missing_key", status_code=303)

    # 4. Success: Render the interactive tutor panel view
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/setup-key")
async def get_setup_page(request: Request, error: str = None):
    return templates.TemplateResponse("setup_key.html", {"request": request, "error": error})


def verify_logged_in(request: Request):
    """Dependency that checks if the authentication token exists in browser cookies."""
    token = request.cookies.get("access_token")
    if not token:
        # If token does not exist, trigger an exception
        raise HTTPException(status_code=303, detail="Not logged in")
    return token


@router.get("/login")
async def get_login_page(request: Request):
    templates = request.app.state.templates

    # 1. Check if the user already has an active login cookie
    token = request.cookies.get("access_token")
    if token and token.startswith("session_"):
        # If they are already logged in, send them straight to the chat app
        return RedirectResponse(url="/chat", status_code=303)

    # 2. If no cookie is found, render the login page as usual
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
async def get_register_page(request: Request):
    templates = request.app.state.templates

    token = request.cookies.get("access_token")
    if token and token.startswith("session_"):
        return RedirectResponse(url="/chat", status_code=303)

    return templates.TemplateResponse("register.html", {"request": request})


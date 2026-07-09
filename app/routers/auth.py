from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & User Profile"]
)

# Instantiate our security service class
auth_service = AuthService()


# =====================================================================
# 1. REGISTER ENDPOINT (Handles HTML Form Submissions)
# =====================================================================
@router.post("/register")
async def register_user(
    first_name: str = Form(...),  # <-- Added Form Parameter
    last_name: str = Form(...),   # <-- Added Form Parameter
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Processes registration HTML form data and creates a secure user profile."""
    email_clean = email.strip().lower()

    # Step 1: Check if email already exists in the database
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered."
        )

    # Step 2: Hash raw text password safely
    hashed_pwd = auth_service.hash_password(password)

    # Step 3: Instantiate user data including first and last name variables
    new_user = User(
        first_name=first_name.strip(),  # <-- Map to DB Column
        last_name=last_name.strip(),    # <-- Map to DB Column
        email=email_clean,
        hashed_password=hashed_pwd,
        encrypted_gemini_key=None
    )

    # Step 4: Commit transaction to SQLite database
    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database save failure. Please try again."
        )

    # Step 5: Smooth Redirect straight to the login screen upon success
    return RedirectResponse(url="/login?success=registered", status_code=303)

# =====================================================================
# 2. UPDATE API KEY ENDPOINT (Handles Setup Form Submissions)
# =====================================================================
@router.post("/update-key")
async def update_api_key(
        gemini_api_key: str = Form(...),
        db: Session = Depends(get_db)
):
    """Allows a logged-in user to save or update their custom Gemini API Key."""
    clean_key = gemini_api_key.strip()

    if not clean_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API Key cannot be blank."
        )


    # --- TEMPORARY IN-LINE FIX UNTIL FULL LOGIN SESSIONS ARE WIRED ---
    # Because we haven't written our JWT session parsing middleware yet,
    # let's find the last registered user in the database to update.
    target_user = db.query(User).order_by(User.id.desc()).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active user profile found to attach this key to."
        )

    # Step 2: Assign the key and commit changes
    try:
        target_user.encrypted_gemini_key = clean_key
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save your API credentials."
        )

    # Step 3: Redirect them rightover to the practice chat workspace
    return RedirectResponse(url="/chat", status_code=303)


# =====================================================================
# 3. LOGIN PROCESSING ENDPOINT (Handles Login Form Submissions)
# =====================================================================
@router.post("/login")
async def login_user(
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    """Verifies user credentials and handles error routing dynamically."""
    email_clean = email.strip().lower()

    # Step 1: Look up user profile
    user = db.query(User).filter(User.email == email_clean).first()

    # Step 2: Fallback redirect if email doesn't exist
    if not user:
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)

    # Step 3: Verify security hash matching values
    is_valid = auth_service.verify_password(password, user.hashed_password)
    if not is_valid:
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)

    # Step 4: Success configuration session
    response = RedirectResponse(url="/chat", status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"session_{user.email}",
        httponly=True,
        max_age=3600
    )
    return response


@router.get("/logout")
async def logout_user():
    """Clears the authentication session cookie and logs out the user."""
    # 1. Redirect to login page
    response = RedirectResponse(url="/login?success=logged_out", status_code=303)

    # 2. Force expire the cookie by deleting it from the client browser
    response.delete_cookie(key="access_token")

    return response
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import our database base configuration and session models
from app.database import models
from app.database.connection import engine # Assuming your db engine setup module exists

# Import our modular APIRouters
from app.routers import auth, chat, page_routers


# =====================================================================
# 1. INITIALIZE DATABASE TABLES (OOP Automatic Migration)
# =====================================================================
try:
    # This instructs SQLAlchemy to check your database and generate
    # the users, chat_sessions, and chat_messages tables if they don't exist yet.
    models.Base.metadata.create_all(bind=engine)
    print("Database structures initialized successfully.")
except Exception as e:
    print(f"Database initialization warning: {e}. Ensure engine is configured.")

# =====================================================================
# 2. CONFIGURE CORE FASTAPI APPLICATION
# =====================================================================
app = FastAPI(
    title="German A1 AI Tutor Platform",
    description="A multi-tenant, BYOK (Bring Your Own Key) web application.",
    version="1.0.0"
)
# Initialize templates here and attach them to app.state so routers can pull them
app.state.templates = Jinja2Templates(directory="templates")

# =====================================================================
# 3. MOUNT MODULAR API AND VIEW ROUTERS
# =====================================================================
# Includes all auth routes (/auth/register, /auth/login, etc.)
app.include_router(auth.router)

# Includes all conversational core engine routes (/chat/send, etc.)
app.include_router(chat.router)

app.include_router(page_routers.router)

# =====================================================================
# LOCAL APPLICATION RUNNER
# =====================================================================
if __name__ == "__main__":
    print("\n--- Starting Lukas German AI Tutor Server ---")
    print("Open http://127.0.0.1:8000 in your browser to test the interface.\n")

    # Run the Uvicorn ASGI server locally with automatic reload turned on
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
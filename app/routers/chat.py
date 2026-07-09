from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User, ChatMessage, ChatSession
from app.services.tutor_engine import GermanTutorEngine

router = APIRouter(
    prefix="/chat",
    tags=["German AI Tutor Engine"]
)


class ChatMessageInput(BaseModel):
    session_id: int
    student_input: str


# =====================================================================
# CHAT EXECUTION ENDPOINT (Handles Async Frontend requests)
# =====================================================================
@router.post("/send")
async def send_chat_message(
        request: Request,
        payload: ChatMessageInput,
        db: Session = Depends(get_db)
):
    """Processes a message turn, updates history, and calls the Gemini Engine."""

    # Step 1: Identify the current user using their session cookie
    token = request.cookies.get("access_token")
    if not token or not token.startswith("session_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again."
        )

    # Extract email back out from our temporary cookie string format
    user_email = token.replace("session_", "")
    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User profile not found."
        )

    # Step 2: Extract their custom Gemini API key
    user_custom_key = user.encrypted_gemini_key
    if not user_custom_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gemini API Key is missing. Please add your key in settings."
        )

    # Step 3: Fetch true past chat history from the database to maintain context
    past_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == payload.session_id)
        .order_by(ChatMessage.timestamp.asc())
        .all()
    )

    # Reconstruct the historical tuple array format that LangChain expects
    runtime_history = []
    for msg in past_messages:
        runtime_history.append(("user", msg.student_input))
        runtime_history.append(("assistant", msg.german_reply))

    # Step 4: Run our LangChain OOP engine with the user's key credentials
    engine = GermanTutorEngine()
    result, error_msg = engine.generate_response(
        student_input=payload.student_input,
        chat_history=runtime_history,
        user_api_key=user_custom_key
    )

    # If the user's key is broken or expired, return a human-readable 422 error
    if error_msg:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_msg
        )

    # Step 5: Save the complete interactive transaction to SQLite
    # Convert lists to clean comma-separated strings for SQLite text storage
    vocab_string = ",".join(result.detected_vocabulary) if result.detected_vocabulary else ""

    new_message_record = ChatMessage(
        session_id=payload.session_id,
        student_input=payload.student_input,
        german_reply=result.german_reply,
        english_translation=result.english_translation,
        corrections_found=result.corrections_found,
        detected_vocabulary=vocab_string
    )

    try:
        db.add(new_message_record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record message history logs."
        )

    # Step 6: Return standard dictionary JSON straight back to the UI frontend interface
    return {
        "status": "success",
        "reply": result.german_reply,
        "translation": result.english_translation,
        "corrections": result.corrections_found,
        "vocabulary": result.detected_vocabulary
    }
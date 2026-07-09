from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# Define the declarative base class for our OOP models
Base = declarative_base()


# Inside app/database/models.py
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(150), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    # --- ADD THESE TWO NEW COLUMNS ---
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    # Store the user's custom key securely.
    # Optional because they might sign up first and add their key later.
    encrypted_gemini_key = Column(Text, nullable=True)


class ChatSession(Base):
    """
    Represents a unique tutoring session for a user.
    One session contains multiple turns of dialogue.
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(100), nullable=False, default="General Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)

    # OOP Relationship: Links a session to all its messages
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """
    Represents an individual turn in the conversation.
    Stores both what the student said and how the AI Tutor evaluated it.
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)

    # The interaction inputs and timeline
    student_input = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # The structured responses parsed from our Gemini Tutor engine
    german_reply = Column(Text, nullable=False)
    english_translation = Column(Text, nullable=False)
    corrections_found = Column(Text, nullable=True)  # Can be null if student made no mistakes
    detected_vocabulary = Column(String(255), nullable=True)  # Stored as a comma-separated string

    # OOP Relationship: Links the message back to its parent session
    session = relationship("ChatSession", back_populates="messages")

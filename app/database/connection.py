from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 1. Define where the database file will be stored locally
# This creates a file named 'german_tutor.db' in your project root folder
DATABASE_URL = settings.DATABASE_URL

# 2. Create the core SQLAlchemy Engine
# 'connect_args' is required ONLY for SQLite to allow multi-threaded FastAPI requests
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 3. Create a Session Local factory
# This factory creates an active transactional database workspace when called
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI Dependency: Yields a database session to a router request
    and safely closes it when the request is completely finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()


class Settings:
    API_KEY: str = os.getenv("API_KEY")
    DATABASE_URL: str= os.getenv("DATABASE_URL")

    if not API_KEY:
        raise ValueError("Missing GEMINI_API_KEY! Please check your .env file.")


settings = Settings()
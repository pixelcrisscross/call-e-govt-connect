import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = f"sqlite:///{(PROJECT_ROOT / 'city_incidents.db').as_posix()}"
configured_database_url = os.getenv("DATABASE_URL")
if configured_database_url and configured_database_url.startswith("sqlite:///./"):
    database_file = configured_database_url.removeprefix("sqlite:///./")
    configured_database_url = f"sqlite:///{(PROJECT_ROOT / database_file).as_posix()}"

class Settings:
    DATABASE_URL = configured_database_url or DEFAULT_DATABASE_URL
    CALLE_API_KEY = os.getenv("CALLE_API_KEY")
    CALLE_PHONE_NUMBER = os.getenv("CALLE_PHONE_NUMBER")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

settings = Settings()
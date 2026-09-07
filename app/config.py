import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./city_incidents.db")
    CALLE_API_KEY = os.getenv("CALLE_API_KEY")
    CALLE_PHONE_NUMBER = os.getenv("CALLE_PHONE_NUMBER")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001/sse")

settings = Settings()
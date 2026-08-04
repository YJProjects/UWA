import os
from pathlib import Path

from dotenv import load_dotenv
import json

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", FRONTEND_ORIGIN).split(",")
    if origin.strip()
]

# Vercel receives the service-account JSON through an encrypted environment
# variable. The path fallback keeps local and Docker development compatible.
FIREBASE_SERVICE_ACCOUNT_JSON = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON"))
FIREAUTH_CREDENTIALS_PATH = Path(
    os.getenv(
        "FIREAUTH_CREDENTIALS_PATH",
        str(BACKEND_DIR.parent / "serviceAccountKey.json"),
    )
).resolve()

BOT_EMAIL = os.getenv("BOT_EMAIL")
BOT_EMAIL_APP_PASSWORD = os.getenv("BOT_EMAIL_APP_PASSWORD")

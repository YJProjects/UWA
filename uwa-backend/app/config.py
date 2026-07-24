import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
DATABASE_URL = os.getenv("DATABASE_URL")
FIREAUTH_CREDENTIALS_PATH = (
    BACKEND_DIR.parent / "serviceAccountKey.json"
).resolve()

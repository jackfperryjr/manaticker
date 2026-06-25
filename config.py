import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
IS_PRODUCTION = bool(os.environ.get("RAILWAY_ENVIRONMENT"))

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY must be set in production")
    SECRET_KEY = "dev-only-insecure-secret-key"

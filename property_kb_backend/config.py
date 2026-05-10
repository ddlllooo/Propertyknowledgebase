import os
from datetime import timedelta

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def _load_backend_env():
    if not load_dotenv:
        return
    from pathlib import Path
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


_load_backend_env()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "property-kb-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "property-kb-jwt-secret-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:123456@localhost:3306/property_kb?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

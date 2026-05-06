import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "property-kb-secret-key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "property-kb-jwt-secret-key")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:123456@localhost:3306/property_kb?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)

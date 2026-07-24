import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'response_connect')}:{os.getenv('DB_PASSWORD', 'response_connect')}"
        f"@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'response_connect')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

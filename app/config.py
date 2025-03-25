import os


DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{
    DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


SECRET = os.getenv("SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv(
    "REDIRECT_URI", "http://127.0.0.1:8000/api/auth/oauth2/authorize")
# https://console.cloud.google.com/apis/

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

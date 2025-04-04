import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Database Configuration
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 3306)
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{
    DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# JWT Configuration
SECRET = os.getenv("SECRET")

# Google OAuth Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
if not CLIENT_ID:
    raise ValueError("CLIENT_ID environment variable is not set")

CLIENT_SECRET = os.getenv("CLIENT_SECRET")
if not CLIENT_SECRET:
    raise ValueError("CLIENT_SECRET environment variable is not set")

REDIRECT_URI = os.getenv("REDIRECT_URI")
if not REDIRECT_URI:
    raise ValueError("REDIRECT_URI environment variable is not set")

# TMDB Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_API_READ_ACCESS_TOKEN = os.getenv("TMDB_API_READ_ACCESS_TOKEN")
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", TMDB_API_READ_ACCESS_TOKEN)
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_HEADERS = {
    "Authorization": f"Bearer {TMDB_API_READ_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

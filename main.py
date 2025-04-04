from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from app.database import engine, Base
from app.config import TMDB_BASE_URL, TMDB_HEADERS
import json

from app.auth.auth import auth_router
from app.api.watchlist import watchlist_router
from app.api.watch_history import history_router
from app.api.movies import movies_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("corsair_stream")

load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite's default port
    "http://127.0.0.1:5173",  # Alternative local frontend
    "http://localhost:8000",  # Backend
    "http://127.0.0.1:8000",  # Alternative backend
    "https://accounts.google.com",  # Google OAuth
    "https://oauth2.googleapis.com",  # Google OAuth API
]


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"{request.method} {request.url.path}?{request.url.query}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Completed in {
                process_time:.2f}s - Status {response.status_code}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(
    watchlist_router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(history_router, prefix="/api/history",
                   tags=["Watch History"])
app.include_router(movies_router, prefix="/api", tags=["Movies"])


@app.get("/")
def get_docs():
    return RedirectResponse("/docs")

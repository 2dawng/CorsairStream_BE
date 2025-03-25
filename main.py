from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


@app.get("/")
def get_docs():
    return RedirectResponse("/docs")


@app.get("/api/search")
def search(query: str, page: int = 1):
    data = {
        "query": query,
        "api_key": TMDB_API_KEY,
        "page": page
    }
    response = requests.get(f"{TMDB_BASE_URL}/search/movie", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))


@app.get("/api/movie/{movie_id}")
def get_movie(movie_id: int):
    data = {
        "api_key": TMDB_API_KEY
    }
    response = requests.get(f"{TMDB_BASE_URL}/movie/{movie_id}", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))


@app.get("/api/movies/{category}")
def get_movies_by_category(category: str, page: int = 1, with_genres: str = None, year: str = None, sort_by: str = None):
    data = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "with_genres": with_genres,
        "year": year,
        "sort_by": sort_by
    }
    response = requests.get(f"{TMDB_BASE_URL}/movie/{category}", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))


@app.get("/api/movie/{movie_id}/credits")
def get_movie_credits(movie_id: int):
    data = {
        "api_key": TMDB_API_KEY
    }
    response = requests.get(
        f"{TMDB_BASE_URL}/movie/{movie_id}/credits", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))


@app.get("/api/movie/{movie_id}/videos")
def get_movie_videos(movie_id: int):
    data = {
        "api_key": TMDB_API_KEY
    }
    response = requests.get(
        f"{TMDB_BASE_URL}/movie/{movie_id}/videos", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))


@app.get("/api/genres/{type}")
def get_genres(type: str):
    data = {
        "api_key": TMDB_API_KEY
    }
    response = requests.get(f"{TMDB_BASE_URL}/genre/{type}/list", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))

# Add similar endpoints for TV shows


@app.get("/api/tv/{category}")
def get_tv_by_category(category: str, page: int = 1, with_genres: str = None, first_air_date_year: str = None, sort_by: str = None):
    data = {
        "api_key": TMDB_API_KEY,
        "page": page,
        "with_genres": with_genres,
        "first_air_date_year": first_air_date_year,
        "sort_by": sort_by
    }
    response = requests.get(f"{TMDB_BASE_URL}/tv/{category}", params=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code,
                            detail=response.json().get("status_message"))

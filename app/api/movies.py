from fastapi import APIRouter, HTTPException
import requests
from app.config import TMDB_BASE_URL, TMDB_HEADERS, TMDB_ACCESS_TOKEN

# Create router
movies_router = APIRouter()


@movies_router.get("/search")
def search_movies(query: str, page: int = 1, include_adult: bool = False, language: str = "en-US", with_genres: str = None, year: str = None, sort_by: str = None):
    """Search for movies using TMDB API"""
    try:
        # Log the incoming request parameters
        print(f"[TMDB API] Received search request with query: {query}")

        # Make sure we're using the correct endpoint and passing all parameters
        url = f"{TMDB_BASE_URL}/search/movie"

        # Create params dictionary with required parameters
        params = {
            "query": query,
            "page": page,
            "include_adult": include_adult,
            "language": language
        }

        # Add optional parameters if provided
        if with_genres:
            params["with_genres"] = with_genres
        if year:
            params["year"] = year
        if sort_by:
            params["sort_by"] = sort_by

        # Log the request for debugging
        print(f"[TMDB API] Request URL: {url}")
        print(f"[TMDB API] Request params: {params}")
        print(f"[TMDB API] Request headers: {TMDB_HEADERS}")

        # Make the request to TMDB API
        response = requests.get(
            url,
            headers=TMDB_HEADERS,
            params=params
        )

        # Log the response status
        print(f"[TMDB API] Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"[TMDB API] Error response: {response.text}")

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[TMDB API] Exception: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching movies: {str(e)}"
        )


@movies_router.get("/{category}")
def get_movies_by_category(category: str, page: int = 1, with_genres: str = None, year: str = None, sort_by: str = None):
    try:
        params = {
            "language": "en-US",
            "page": page
        }

        if with_genres:
            params["with_genres"] = with_genres
        if year:
            params["year"] = year
        if sort_by:
            params["sort_by"] = sort_by

        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{category}",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching movies: {str(e)}")


@movies_router.get("/movie/{movie_id}")
def get_movie_details(movie_id: int):
    try:
        params = {
            "language": "en-US",
            "append_to_response": "videos,credits,similar"
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}",
            headers=TMDB_HEADERS,
            params=params
        )

        if response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Movie not found"
            )

        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with ID {movie_id} not found"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching movie details: {str(e)}"
        )


@movies_router.get("/movie/{movie_id}/images")
def get_movie_images(movie_id: int):
    try:
        # Log the request
        print(f"[TMDB API] Fetching images for movie ID: {movie_id}")

        # Set up headers with authorization
        headers = {
            "Authorization": f"Bearer {TMDB_ACCESS_TOKEN}",
            "accept": "application/json"
        }

        # Set up parameters
        params = {
            "language": "en"
        }

        # Make the request to TMDB API
        url = f"{TMDB_BASE_URL}/movie/{movie_id}/images"
        print(f"[TMDB API] Request URL: {url}")
        print(f"[TMDB API] Request headers: {headers}")
        print(f"[TMDB API] Request params: {params}")

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        # Log the response status
        print(f"[TMDB API] Response status: {response.status_code}")

        # Log the response data
        if response.status_code == 200:
            data = response.json()
            print(f"[TMDB API] Response data: {data}")
            return data
        else:
            print(f"[TMDB API] Error response: {response.text}")
            response.raise_for_status()

    except requests.RequestException as e:
        print(f"[TMDB API] Exception: {str(e)}")
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"Images for movie with ID {movie_id} not found"
            )
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching movie images: {str(e)}"
        )


@movies_router.get("/movie/{movie_id}/watch/providers")
def get_movie_watch_providers(movie_id: int):
    """Get streaming availability for a movie"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/watch/providers",
            headers=TMDB_HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching watch providers: {str(e)}"
        )


@movies_router.get("/discover/streaming/{provider_id}")
def get_movies_by_provider(
    provider_id: int,
    page: int = 1,
    region: str = "US"
):
    """Get movies available on a specific streaming service"""
    try:
        params = {
            "language": "en-US",
            "page": page,
            "watch_region": region,
            "with_watch_providers": provider_id,
            "watch_monetization_types": "flatrate"
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching streaming movies: {str(e)}"
        )


@movies_router.get("/watch/providers")
def get_watch_providers(region: str = "US"):
    """Get list of available streaming providers"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/watch/providers/movie",
            headers=TMDB_HEADERS,
            params={"watch_region": region}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching providers: {str(e)}"
        )


@movies_router.get("/movie/{movie_id}/credits")
def get_movie_credits(movie_id: int):
    """Get credits (cast & crew) for a movie"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/credits",
            headers=TMDB_HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching movie credits: {str(e)}"
        )


@movies_router.get("/movie/{movie_id}/videos")
def get_movie_videos(movie_id: int):
    """Get videos (trailers, teasers, etc.) for a movie"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/videos",
            headers=TMDB_HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching movie videos: {str(e)}"
        )


@movies_router.get("/movie/{movie_id}/similar")
def get_similar_movies(movie_id: int):
    """Get similar movies recommendations"""
    try:
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{movie_id}/similar",
            headers=TMDB_HEADERS
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching similar movies: {str(e)}"
        )


@movies_router.get("/genres/movie")
def get_movie_genres():
    """Get list of movie genres"""
    try:
        params = {
            "language": "en-US"
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching genres: {str(e)}"
        )


@movies_router.get("/discover/genre/{genre_id}")
def get_movies_by_genre(genre_id: int, page: int = 1):
    """Get movies by genre"""
    try:
        params = {
            "language": "en-US",
            "page": page,
            "with_genres": genre_id,
            "sort_by": "popularity.desc"
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/discover/movie",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching movies by genre: {str(e)}"
        )


@movies_router.get("/now_playing")
def get_now_playing(page: int = 1):
    """Get movies now playing in theaters"""
    try:
        params = {
            "language": "en-US",
            "page": page
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/movie/now_playing",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching now playing movies: {str(e)}"
        )


@movies_router.get("/genres/mapping")
def get_genre_mapping():
    """Get mapping of genre names to IDs"""
    try:
        params = {
            "language": "en-US"
        }

        response = requests.get(
            f"{TMDB_BASE_URL}/genre/movie/list",
            headers=TMDB_HEADERS,
            params=params
        )
        response.raise_for_status()
        genres = response.json().get('genres', [])

        # Create a mapping of genre names to IDs
        genre_mapping = {genre['name'].lower(): genre['id']
                         for genre in genres}
        return genre_mapping
    except requests.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching genre mapping: {str(e)}"
        )

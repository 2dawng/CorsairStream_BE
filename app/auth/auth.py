import json
from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import requests
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse

from app.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, SECRET
from app.database import SessionLocal
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    id: int
    username: str
    email: str
    profile_picture: Optional[str] = None


class TokenRequest(BaseModel):
    code: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials,
                             SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

auth_router = APIRouter(tags=["Auth"])


@auth_router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "created_at": db_user.created_at
    }


@auth_router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Email not found")

    if not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    user_data = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "profile_picture": db_user.profile_picture,
        "created_at": db_user.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "profile_picture": db_user.profile_picture
    }


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(current_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "profile_picture": current_user.profile_picture
    }


@auth_router.get("/google/login")
def google_login():
    """Initiate Google OAuth flow"""
    if not CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth client ID not configured"
        )

    auth_params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }

    # Build the authorization URL with proper URL encoding
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{
        urlencode(auth_params)}"

    return {"auth_url": auth_url}


@auth_router.get('/oauth2/callback')
async def oauth2_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Get the code from query parameters
        code = request.query_params.get('code')
        if not code:
            raise HTTPException(
                status_code=400,
                detail="No authorization code found"
            )

        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
        }

        # Exchange code for tokens
        token_response = requests.post(token_url, data=data)

        if not token_response.ok:
            error_detail = token_response.json()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to exchange code: {error_detail}"
            )

        token_data = token_response.json()

        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f"Bearer {token_data['access_token']}"}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        # Extract user information
        email = user_info.get("email")
        # Use email prefix if name not provided
        name = user_info.get("name", email.split('@')[0])
        picture = user_info.get("picture")

        if not email:
            raise HTTPException(
                status_code=400, detail="Email not provided by Google")

        # Check if user exists
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user:
            # Create new user with Google data
            db_user = User(
                username=name,
                email=email,
                profile_picture=picture,
                # Empty password for OAuth users
                hashed_password=pwd_context.hash(""),
                is_active=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        else:
            print(f"\nFound existing user with email: {email}")

        # Create tokens
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

        # Redirect to frontend with tokens
        response_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "profile_picture": db_user.profile_picture
            }
        }

        # Redirect to frontend
        frontend_url = "http://localhost:5173/auth/google/callback"

        # Properly encode all parameters
        redirect_params = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": json.dumps(response_data["user"])
        }

        # Redirect to frontend
        redirect_url = f"{frontend_url}?{urlencode(redirect_params)}"

        return RedirectResponse(
            url=redirect_url,
            status_code=302
        )

    except requests.RequestException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error during Google OAuth: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

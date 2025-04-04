from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Watchlist, WatchHistory
from app.auth.auth import get_current_user


def check_watchlist_owner(watchlist_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check if user owns the watchlist"""
    watchlist = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id).first()
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    if current_user.id != watchlist.user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this watchlist")
    return watchlist


def check_watch_history_owner(content_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check if user owns the watch history entry"""
    history = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id,
        WatchHistory.content_id == content_id
    ).first()
    if not history:
        raise HTTPException(status_code=404, detail="Watch history not found")
    return history


def check_admin(current_user: User = Depends(get_current_user)):
    """Check if user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def create_authenticated_router(tag: str):
    """Create a router with authentication dependency"""
    from fastapi import APIRouter
    return APIRouter(
        tags=[tag],
        dependencies=[Depends(get_current_user), Depends(HTTPBearer())]
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WatchHistory
from app.auth.utils import check_watch_history_owner, create_authenticated_router
from app.auth.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create router with authentication dependency
history_router = create_authenticated_router("Watch History")


class WatchHistoryCreate(BaseModel):
    content_id: str
    completed: bool = False


class WatchHistoryResponse(BaseModel):
    user_id: int
    content_id: str
    watched_at: str
    completed: bool

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


@history_router.post("/", response_model=WatchHistoryResponse)
def create_watch_history(
    history: WatchHistoryCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new watch history entry"""
    print(f"Creating watch history for user {
          current_user.id} with content_id {history.content_id}")

    # Check if the entry already exists
    existing_history = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id,
        WatchHistory.content_id == history.content_id
    ).first()

    if existing_history:
        # If it exists, update the watched_at timestamp and completed status
        print(f"Updating existing watch history: {existing_history}")
        existing_history.watched_at = datetime.utcnow()
        existing_history.completed = history.completed
        db.commit()
        db.refresh(existing_history)

        # Convert the response to a dictionary with the watched_at field as a string
        response_dict = {
            "user_id": existing_history.user_id,
            "content_id": existing_history.content_id,
            "watched_at": existing_history.watched_at.isoformat() if existing_history.watched_at else None,
            "completed": existing_history.completed
        }
        return response_dict

    # If it doesn't exist, create a new entry
    db_history = WatchHistory(
        user_id=current_user.id,
        content_id=history.content_id,
        completed=history.completed
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    print(f"Created watch history: {db_history}")

    # Convert the response to a dictionary with the watched_at field as a string
    response_dict = {
        "user_id": db_history.user_id,
        "content_id": db_history.content_id,
        "watched_at": db_history.watched_at.isoformat() if db_history.watched_at else None,
        "completed": db_history.completed
    }
    return response_dict


@history_router.get("/", response_model=List[WatchHistoryResponse])
def get_user_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all watch history for the current user"""
    histories = db.query(WatchHistory).filter(
        WatchHistory.user_id == current_user.id).all()

    # Convert the response to a list of dictionaries with the watched_at field as a string
    response_list = [
        {
            "user_id": history.user_id,
            "content_id": history.content_id,
            "watched_at": history.watched_at.isoformat() if history.watched_at else None,
            "completed": history.completed
        }
        for history in histories
    ]
    return response_list


@history_router.get("/{content_id}", response_model=WatchHistoryResponse)
def get_watch_history(
    content_id: str,
    history: WatchHistory = Depends(check_watch_history_owner),
    db: Session = Depends(get_db)
):
    """Get a specific watch history entry"""
    # Convert the response to a dictionary with the watched_at field as a string
    response_dict = {
        "user_id": history.user_id,
        "content_id": history.content_id,
        "watched_at": history.watched_at.isoformat() if history.watched_at else None,
        "completed": history.completed
    }
    return response_dict


@history_router.put("/{content_id}", response_model=WatchHistoryResponse)
def update_watch_history(
    content_id: str,
    completed: bool,
    history: WatchHistory = Depends(check_watch_history_owner),
    db: Session = Depends(get_db)
):
    """Update a watch history entry"""
    history.completed = completed
    db.commit()
    db.refresh(history)

    # Convert the response to a dictionary with the watched_at field as a string
    response_dict = {
        "user_id": history.user_id,
        "content_id": history.content_id,
        "watched_at": history.watched_at.isoformat() if history.watched_at else None,
        "completed": history.completed
    }
    return response_dict


@history_router.delete("/{content_id}", response_model=WatchHistoryResponse)
def delete_watch_history(
    content_id: str,
    history: WatchHistory = Depends(check_watch_history_owner),
    db: Session = Depends(get_db)
):
    """Delete a watch history entry"""
    db.delete(history)
    db.commit()

    # Convert the response to a dictionary with the watched_at field as a string
    response_dict = {
        "user_id": history.user_id,
        "content_id": history.content_id,
        "watched_at": history.watched_at.isoformat() if history.watched_at else None,
        "completed": history.completed
    }
    return response_dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Watchlist
from app.auth.utils import check_watchlist_owner, create_authenticated_router
from app.auth.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create router with authentication dependency
watchlist_router = create_authenticated_router("Watchlist")


class WatchlistCreate(BaseModel):
    content_id: str

    class Config:
        json_schema_extra = {
            "example": {
                "content_id": "123"
            }
        }


class WatchlistResponse(BaseModel):
    id: int
    user_id: int
    content_id: str
    added_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


@watchlist_router.post("/", response_model=WatchlistResponse)
def create_watchlist(
    watchlist: WatchlistCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new watchlist item"""
    try:
        # Check if movie already exists in user's watchlist
        existing_item = db.query(Watchlist).filter(
            Watchlist.user_id == current_user.id,
            Watchlist.content_id == watchlist.content_id
        ).first()

        if existing_item:
            raise HTTPException(
                status_code=400,
                detail="Movie already in watchlist"
            )

        # Create new watchlist item
        new_watchlist = Watchlist(
            user_id=current_user.id,
            content_id=watchlist.content_id
        )

        db.add(new_watchlist)
        db.commit()
        db.refresh(new_watchlist)
        return new_watchlist

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating watchlist: {str(e)}"
        )


@watchlist_router.get("/", response_model=List[WatchlistResponse])
def get_user_watchlist(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all watchlist items for the current user"""
    return db.query(Watchlist).filter(Watchlist.user_id == current_user.id).all()


@watchlist_router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(
    watchlist_id: int,
    watchlist: Watchlist = Depends(check_watchlist_owner),
    db: Session = Depends(get_db)
):
    """Get a specific watchlist item"""
    return watchlist


@watchlist_router.delete("/{content_id}/")
def delete_watchlist(
    content_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a watchlist item by content_id"""
    watchlist_item = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.id,
        Watchlist.content_id == content_id
    ).first()

    if not watchlist_item:
        raise HTTPException(
            status_code=404,
            detail="Watchlist item not found"
        )

    db.delete(watchlist_item)
    db.commit()
    return {"message": "Watchlist item deleted successfully"}

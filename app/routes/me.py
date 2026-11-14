from fastapi import APIRouter, HTTPException
from sqlmodel import col, select

from app.auth import CurrentUser
from app.db import SessionDep
from app.models import Profile, WatchlistItem
from app.schemas import ProfileIn, UserPublic, WatchlistIn, WatchlistOut

router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser):
    return user


@router.get("/me/profile", response_model=ProfileIn)
def get_profile(user: CurrentUser, session: SessionDep):
    return session.get(Profile, user.id)


@router.put("/me/profile", response_model=ProfileIn)
def put_profile(data: ProfileIn, user: CurrentUser, session: SessionDep):
    profile = session.get(Profile, user.id)
    profile.sqlmodel_update(data.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

@router.get("/watchlist", response_model=list[WatchlistOut])
def list_watchlist(user: CurrentUser, session: SessionDep):
    query = select(WatchlistItem).where(WatchlistItem.user_id == user.id).order_by(col(WatchlistItem.id))
    return session.exec(query).all()

@router.post("/watchlist", response_model=WatchlistOut, status_code=201)
def add_watchlist(data: WatchlistIn, user: CurrentUser, session: SessionDep):
    board = data.board.lower()
    duplicate = select(WatchlistItem).where(WatchlistItem.user_id == user.id, WatchlistItem.ats == data.ats, WatchlistItem.board == board)
    if session.exec(duplicate).first():
        raise HTTPException(status_code=409, detail=f"{data.ats}:{board} is already on your watchlist")
    item = WatchlistItem(user_id=user.id, ats=data.ats, board=board)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.delete("/watchlist/{item_id}", status_code=204)
def delete_watchlist(item_id: int, user: CurrentUser, session: SessionDep):
    item = session.get(WatchlistItem, item_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    session.delete(item)
    session.commit()
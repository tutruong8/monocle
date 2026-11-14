from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.auth import create_token, hash_pass, verify_pass
from app.db import SessionDep
from app.models import Profile, User
from app.schemas import Token, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic, status_code=201)
def register(data: UserCreate, session: SessionDep):
    email = data.email.lower()
    if session.exec(select(User).where(User.email == email)).first():
        raise HTTPException(status_code=409, detail=f"User with email {email!r} already exists")
    user = User(email=email, pass_hash=hash_pass(data.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    session.add(Profile(user_id=user.id))
    session.commit()
    return user

@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user = session.exec(select(User).where(User.email == form.username.lower())).first()
    if not verify_pass(form.password, user.pass_hash if user else None):
        raise HTTPException(status_code=401, detail="Invalid email or password", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_token(user.id))
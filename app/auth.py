import os
from datetime import timedelta
from typing import Annotated
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from app.db import SessionDep
from app.models import User, utc_now

SECRET = os.environ.get("JWT_SECRET", "")
if len(SECRET) < 32:
    raise RuntimeError("JWT_SECRET must be at least 32 characters long")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pass_hash = PasswordHash.recommended()
DUMMY_HASH = pass_hash.hash("dummy_password")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_pass(password: str) -> str:
    return pass_hash.hash(password)

def verify_pass(password: str, hashed: str | None) -> bool:
    return pass_hash.verify(password, hashed or DUMMY_HASH) and hashed is not None

def create_token(user_id: int) -> str:
    now = utc_now()
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)

def current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    unauthorized = HTTPException(status_code=401, detail="Not logged in or tokens have expired", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise unauthorized
    user = session.get(User, user_id)
    if not user:
        raise unauthorized
    return user

CurrentUser = Annotated[User, Depends(current_user)]
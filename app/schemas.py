from datetime import date
from typing import Annotated, Literal
from pydantic import EmailStr, StringConstraints, model_validator
from sqlmodel import Field, SQLModel

BoardName = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9_-]{1,100}$")]

class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserPublic(SQLModel):
    id: int
    email: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class ProfileIn(SQLModel):
    levels: list[Literal["new_grad", "intern"]] = Field(default=["new_grad"], min_length=1)
    degree: Literal["bachelors", "masters", "phd"] = "bachelors"
    grad_date: date | None = None
    ms_start: date | None = None
    max_years: int = Field(default=1, ge=0, le=15)
    locations: list[str] = Field(default_factory=list)
    remote_ok: bool = True
    stack: list[str] = Field(default_factory=list)
    @model_validator(mode="after")
    def ms_after_grad(self):
        if self.ms_start and self.grad_date and self.ms_start < self.grad_date:
            raise ValueError("ms_start must be after grad_date")
        return self

class WatchlistIn(SQLModel):
    ats: Literal["greenhouse", "ashby", "lever"]
    board: BoardName

class WatchlistOut(WatchlistIn):
    id: int
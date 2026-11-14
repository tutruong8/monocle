from datetime import date, datetime, timezone
from sqlalchemy import JSON, Column, DateTime, UniqueConstraint
from sqlmodel import Field, SQLModel

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Posting(SQLModel, table=True):
    __tablename__ = "postings"

    id: int | None = Field(default=None, primary_key=True)
    source: str
    external_id: str
    url_norm: str = Field(unique=True)
    company: str
    title: str
    level: str = "unknown"
    terms: str | None = None
    locations: str | None = None
    description: str | None = None
    first_seen_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    last_seen_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    closed_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))

class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: int | None = Field(default=None, primary_key=True)
    source: str
    started_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))
    finished_at: datetime | None = Field(default=None, sa_type=DateTime(timezone=True))
    ok: bool = False
    counts: dict = Field(default_factory=dict, sa_column=Column(JSON))
    error: str | None = None

class User(SQLModel, table = True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    pass_hash: str
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

class Profile(SQLModel, table = True):
    __tablename__ = "profiles"
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    levels: list[str] = Field(default_factory=lambda: ["new_grad"], sa_column=Column(JSON))
    degree: str = "bachelors"
    grad_date: date | None = None
    ms_start: date | None = None
    max_years: int = 1
    locations: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    remote_ok: bool = True
    stack: list[str] = Field(default_factory=list, sa_column=Column(JSON))

class WatchlistItem(SQLModel, table=True):
    __tablename__ = "watchlist"
    __table_args__ = (UniqueConstraint("user_id", "ats", "board"),)
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    ats: str
    board: str
    created_at: datetime = Field(default_factory=utc_now, sa_type=DateTime(timezone=True))

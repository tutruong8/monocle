from datetime import datetime, timezone
from sqlalchemy import JSON, Column, DateTime
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
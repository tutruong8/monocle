import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import httpx
from fastapi import FastAPI, HTTPException
from sqlmodel import create_engine, Field, Session, SQLModel, col, func, select
from sqlalchemy.dialects.postgresql import insert

engine = create_engine(os.environ["DATABASE_URL"])
USER_AGENT = f"monocle/0.1 (student project; {os.environ.get('CONTACT_EMAIL', 'no-contact')})"

class Posting(SQLModel, table=True):
    __tablename__ = "postings"

    id: int | None = Field(default=None, primary_key=True)
    source: str
    external_id: str
    url_norm: str = Field(unique=True)
    company: str
    title: str
    location: str | None = None
    first_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="monocle", lifespan=lifespan)

def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (k, v) 
        for k, v in parse_qsl(parts.query)
        if not k.startswith("utm_") and k not in {"gh_src", "source", "ref"}
    ]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/admin/ingest/greenhouse/{board}")
def ingest_greenhouse(board: str):
    response = httpx.get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", headers={"User-Agent": USER_AGENT}, timeout=10)
    if response.status_code == 404:
        raise HTTPException(status_code=response.status_code, detail=f"Greenhouse API returned {response.status_code}, no Greenhouse board found for {board!r}")
    response.raise_for_status()

    now = datetime.now(timezone.utc)
    rows = [
        {
            "source": "greenhouse",
            "external_id": str(job["id"]),
            "url_norm": normalize_url(job["absolute_url"]),
            "company": board,
            "title": job["title"],
            "location": (job.get("location") or {}).get("name"),
            "first_seen_at": now,
            "last_seen_at": now,
        }
        for job in response.json().get("jobs", [])
    ]
    if not rows:
        return {"fetched": 0, "new": 0}

    stmt = insert(Posting).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["url_norm"],
        set_={
            "title": stmt.excluded.title,
            "last_seen_at": stmt.excluded.last_seen_at
        },
        )
    with Session(engine) as session:
        before = session.exec(select(func.count()).select_from(Posting)).one()
        session.exec(stmt)
        session.commit()
        after = session.exec(select(func.count()).select_from(Posting)).one()
    return {"fetched": len(rows), "new": after - before}


@app.get("/postings")
def list_postings(limit: int = 50):
    with Session(engine) as session:
        query = select(Posting).order_by(col(Posting.first_seen_at).desc()).limit(limit)
        return session.exec(query).all()
from contextlib import asynccontextmanager
from enum import Enum  

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, col, select

from app.db import get_session, init_db
from app.ingest import run_ingest
from app.models import Posting, Run
from app.sources.boards import fetch_ashby, fetch_greenhouse, fetch_lever
from app.sources.http import SourceNotFoundError
from app.sources.simplify import fetch_simplify

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Monocle", lifespan=lifespan)

BOARD_FETCHERS = {"greenhouse": fetch_greenhouse, "ashby": fetch_ashby, "lever": fetch_lever}


class Ats(str, Enum):
    greenhouse = "greenhouse"
    ashby = "ashby"
    lever = "lever"


class Level(str, Enum):
    new_grad = "new_grad"
    intern = "intern"

def _ingest(session: Session, source: str, fetch) -> Run:
    try:
        return run_ingest(session, source, fetch)
    except SourceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Source {source!r} not found")
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Source {source!r} failed to respond: {e}")


@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/admin/ingest/simplify/{level}", response_model=Run)
def ingest_simplify(level: Level, session: Session = Depends(get_session)):
    return _ingest(session, f"simplify_{level.value}", lambda: fetch_simplify(level.value))

@app.post("/admin/ingest/{ats}/{board}", response_model=Run)
def ingest_board(ats: Ats, board: str, session: Session = Depends(get_session)):
    fetch = BOARD_FETCHERS.get(ats.value)
    return _ingest(session, f"{ats.value}_{board}", lambda: fetch(board))

@app.get("/runs", response_model=list[Run])
def list_runs(limit: int = 20, session: Session = Depends(get_session)):
    query = select(Run).order_by(col(Run.started_at).desc()).limit(limit)
    return session.exec(query).all()

@app.get("/postings", response_model=list[Posting])
def list_postings(limit: int = 50, level: Level | None = None, include_closed: bool = False, session: Session = Depends(get_session)):
    query = select(Posting)
    if level:
        query = query.where(col(Posting.level) == level.value)
    if not include_closed:
        query = query.where(col(Posting.closed_at).is_(None))
    return session.exec(query.order_by(col(Posting.first_seen_at).desc()).limit(limit)).all()
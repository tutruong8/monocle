from collections.abc import Callable
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert 
from sqlmodel import Session, col, select
from app.models import Posting, Run, utc_now

TRACKING_PARAMS = {"gh_src", "source", "ref"}
BATCH = 1000

def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    query = [
        (k, v) 
        for k, v in parse_qsl(parts.query)
        if not k.startswith("utm_") and k not in TRACKING_PARAMS
    ]
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), urlencode(query), ""))

def upsert_posting(session: Session, source: str, row: list[dict], seen_at: datetime) -> dict:
    by_url = {normalize_url(r["url"]): r for r in row}
    urls = list(by_url)

    existing = 0
    for i in range(0, len(urls), BATCH):
        chunk = urls[i:i+BATCH]
        existing += len(session.exec(select(Posting.url_norm).where(col(Posting.url_norm).in_(chunk))).all())
        values = [
        {**{k: v for k, v in row.items() if k != "url"},
            "source": source,
            "url_norm": url,
            "first_seen_at": seen_at,
            "last_seen_at": seen_at,
        } for url, row in by_url.items()
        ]
    for i in range(0, len(values), BATCH):
        stmt = insert(Posting).values(values[i:i+BATCH])
        stmt = stmt.on_conflict_do_update(
            index_elements=["url_norm"],
            set_= {
                "title": stmt.excluded.title,
                "last_seen_at": stmt.excluded.last_seen_at,
                "closed_at": None,
            },
        )
        session.exec(stmt)
    return {"fetched": len(row), "unique": len(values), "new": len(row) - existing}

def close_missing(session: Session, source: str, run_started: datetime) -> int:
    stmt = (
        update(Posting)
        .where(col(Posting.source) == source)
        .where(col(Posting.closed_at) == None)
        .where(col(Posting.last_seen_at) < run_started)
        .values(closed_at=utc_now())
    )
    return session.exec(stmt).rowcount

def run_ingest(session: Session, source: str, fetch: Callable[[], list[dict]]) -> Run:
    run = Run(source=source)
    session.add(run)
    session.commit()
    session.refresh(run)
    try:
        rows = fetch()
        counts = upsert_posting(session, source, rows, seen_at=run.started_at)
        counts["closed"] = close_missing(session, source, run.started_at)
        run.ok = True
        run.counts = counts
    except Exception as exc:
        session.rollback()
        run.error = f"{type(exc).__name__}: {exc}"[:500]
        raise
    finally:
        run.finished_at = utc_now()
        session.add(run)
        session.commit()
        session.refresh(run)
    return run

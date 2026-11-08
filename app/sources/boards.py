from app.sources.http import polite_get


def fetch_greenhouse(board: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    jobs = polite_get(url).json().get("jobs", [])
    return [
        {
            "external_id": str(job["id"]),
            "url": job["absolute_url"],
            "company": board,
            "title": job["title"],
            "locations": (job.get("location") or {}).get("name"),
            "description": job.get("content"),
        }
        for job in jobs
    ]


def fetch_ashby(board: str) -> list[dict]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
    jobs = polite_get(url).json().get("jobs", [])
    return [
        {
            "external_id": job["id"],
            "url": job.get("jobUrl") or job["applyUrl"],
            "company": board,
            "title": job["title"],
            "locations": "; ".join(
                [job.get("location") or ""] + [s["location"] for s in job.get("secondaryLocations") or []]
            ).strip("; ") or None,
            "description": job.get("descriptionPlain"),
        }
        for job in jobs
        if job.get("isListed", True)
    ]


def fetch_lever(board: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    jobs = polite_get(url).json()
    return [
        {
            "external_id": job["id"],
            "url": job["hostedUrl"],
            "company": board,
            "title": job["text"],
            "locations": (job.get("categories") or {}).get("location"),
            "description": job.get("descriptionPlain"),
        }
        for job in jobs
    ]
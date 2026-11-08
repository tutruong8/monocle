import os

from app.sources.http import polite_get

LIST_URLS = {
    "new_grad": os.environ.get(
        "SIMPLIFY_NEW_GRAD_URL",
        "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json",
    ),
    "intern": os.environ.get(
        "SIMPLIFY_INTERN_URL",
        "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/.github/scripts/listings.json",
    ),
}


def fetch_simplify(level: str) -> list[dict]:
    items = polite_get(LIST_URLS[level]).json()
    return [
        {
            "external_id": item["id"],
            "url": item["url"],
            "company": item["company_name"],
            "title": item["title"],
            "level": level,
            "terms": "; ".join(item.get("terms") or []) or None,
            "locations": "; ".join(item.get("locations") or []) or None,
        }
        for item in items
        if item.get("active") and item.get("is_visible", True)
    ]
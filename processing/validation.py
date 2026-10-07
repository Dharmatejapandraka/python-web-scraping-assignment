"""Validation rules for standardized records."""
from __future__ import annotations

import math
from urllib.parse import urlparse

VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record: dict) -> list[str]:
    problems: list[str] = []
    if record.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")
    if not record.get("name_or_title"):
        problems.append("missing_name_or_title")

    url = record.get("source_url") or ""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        problems.append("invalid_url")

    price = record.get("price")
    if price is not None and (not isinstance(price, (int, float)) or isinstance(price, bool) or not math.isfinite(price) or price < 0):
        problems.append("invalid_price")

    rating = record.get("rating")
    if rating is not None and (not isinstance(rating, int) or rating not in {1, 2, 3, 4, 5}):
        problems.append("invalid_rating")

    if record.get("source") == "Quotes to Scrape" and not record.get("author"):
        problems.append("missing_author")

    return problems

"""Pure cleaning/normalization functions."""
from __future__ import annotations

import re
from urllib.parse import urlparse

RATING_MAP = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def clean_text(value):
    if value is None:
        return None
    text = " ".join(str(value).replace("\xa0", " ").split())
    return text or None


def strip_quotes(value):
    text = clean_text(value)
    if not text:
        return None
    return text.strip("“”\"'") or None


def clean_price(raw):
    if raw is None or str(raw).strip() == "":
        return None
    match = re.search(r"\d+(?:\.\d+)?", str(raw).replace(",", ""))
    return float(match.group()) if match else None


def clean_rating(raw):
    if raw is None:
        return None
    for word in str(raw).lower().split():
        if word in RATING_MAP:
            return RATING_MAP[word]
    return None


def clean_tags(tags):
    if tags is None:
        return None
    if isinstance(tags, str):
        values = [item.strip() for item in tags.split(";") if item.strip()]
    else:
        values = [clean_text(item).lower() for item in tags if clean_text(item)]
    values = sorted(set(values))
    return ";".join(values) if values else None


def normalize_url(value):
    value = clean_text(value)
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


def clean_record(record: dict) -> dict:
    cleaned = dict(record)
    cleaned["source"] = clean_text(cleaned.get("source"))
    cleaned["source_url"] = normalize_url(cleaned.get("source_url"))
    cleaned["name_or_title"] = strip_quotes(cleaned.get("name_or_title"))
    cleaned["category"] = clean_text(cleaned.get("category"))
    cleaned["price"] = clean_price(cleaned.get("price"))
    cleaned["rating"] = clean_rating(cleaned.get("rating"))
    cleaned["author"] = clean_text(cleaned.get("author"))
    cleaned["tags"] = clean_tags(cleaned.get("tags"))
    cleaned["description"] = clean_text(cleaned.get("description"))
    return cleaned

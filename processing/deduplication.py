"""Deterministic duplicate detection using normalized fingerprints."""
from __future__ import annotations

import hashlib
import re


def _normalize_key(value) -> str:
    value = str(value or "").lower()
    value = re.sub(r"[^\w\s]", "", value, flags=re.UNICODE)
    return " ".join(value.split())


def make_fingerprint(record: dict) -> str:
    source = _normalize_key(record.get("source"))
    if record.get("source") == "Books to Scrape":
        key = f"{source}|{_normalize_key(record.get('name_or_title'))}"
    else:
        quote = _normalize_key(record.get("name_or_title"))[:50]
        key = f"{source}|{_normalize_key(record.get('author'))}|{quote}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def find_duplicates(records: list[dict]):
    seen: set[str] = set()
    unique: list[dict] = []
    duplicates: list[dict] = []
    for record in records:
        fingerprint = make_fingerprint(record)
        if fingerprint in seen:
            duplicates.append(record)
        else:
            seen.add(fingerprint)
            unique.append(record)
    return unique, duplicates

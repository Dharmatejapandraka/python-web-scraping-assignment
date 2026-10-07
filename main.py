"""End-to-end entry point for the multi-source scraping assignment."""
from __future__ import annotations

import csv
import json
import logging
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
LOG_DIR = ROOT / "logs"
CSV_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"

FIELDNAMES = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "scraped_at"
]


def configure_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handlers = [
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )


def write_csv(records: list[dict]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def write_json(data: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)


def process_source(scraper, started_at: str):
    logger = logging.getLogger(__name__)
    stats = {
        "raw_records": 0,
        "cleaned_records": 0,
        "rejected_records": 0,
        "rejected_by_reason": {},
        "duplicates": 0,
        "status": "success",
    }
    try:
        raw = scraper.scrape()
        stats["raw_records"] = len(raw)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unexpected source failure: %s", exc)
        stats["status"] = "failed"
        return [], stats

    cleaned: list[dict] = []
    for record in raw:
        item = clean_record(record)
        problems = validate_record(item)
        if problems:
            stats["rejected_records"] += 1
            for reason in problems:
                stats["rejected_by_reason"][reason] = stats["rejected_by_reason"].get(reason, 0) + 1
            logger.warning("Rejected %s record: %s", scraper.source_name, problems)
            continue
        item["scraped_at"] = started_at
        cleaned.append(item)

    stats["cleaned_records"] = len(cleaned)
    unique, duplicates = find_duplicates(cleaned)
    stats["duplicates"] = len(duplicates)
    return unique, stats


def main() -> int:
    configure_logging()
    logger = logging.getLogger(__name__)
    start = time.perf_counter()
    start_dt = datetime.now(timezone.utc)
    scraped_at = start_dt.isoformat()
    logger.info("Starting scraping pipeline")

    sources = [BooksScraper(), QuotesScraper()]
    all_records: list[dict] = []
    source_stats: dict = {}

    for scraper in sources:
        records, stats = process_source(scraper, scraped_at)
        all_records.extend(records)
        source_stats[scraper.source_name] = stats

    # A second global deduplication protects against duplicates across sources too.
    unique_records, global_duplicates = find_duplicates(all_records)
    if global_duplicates:
        logger.warning("Global duplicate pass removed %d records", len(global_duplicates))

    write_csv(unique_records)
    end_dt = datetime.now(timezone.utc)
    duration = round(time.perf_counter() - start, 3)

    summary = {
        "run": {
            "started_at": start_dt.isoformat(),
            "ended_at": end_dt.isoformat(),
            "duration_seconds": duration,
        },
        "sources": source_stats,
        "global_duplicates_removed": len(global_duplicates),
        "final_record_count": len(unique_records),
        "output_files": ["output/final_dataset.csv", "output/summary_report.json", "logs/scraper.log"],
    }
    write_json(summary)
    logger.info("Completed: %d final records", len(unique_records))
    logger.info("CSV: %s", CSV_PATH)
    logger.info("Summary: %s", SUMMARY_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

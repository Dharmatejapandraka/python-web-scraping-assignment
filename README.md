# Multi-Source Web Scraping & Data Consolidation

## 1. Overview

This project implements the Python web scraping interview assessment using the two required public practice websites:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline follows:

**Scrape → Clean → Validate → Deduplicate → Consolidate → Save**

It produces a consolidated CSV, a JSON summary report, and a timestamped log.

## 2. Requirements

- Python 3.10–3.12 recommended by the assessment
- Internet connection
- `requests`
- `beautifulsoup4`
- `lxml`
- `pytest`

## 3. Setup

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows Command Prompt:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 4. Run

```bash
python main.py
```

Generated files:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## 5. Pagination

Both source scrapers start from the home page and follow `li.next > a` using `urllib.parse.urljoin`. Page numbers are never hard-coded. If a request fails after the configured retry attempts, that source is stopped gracefully and the other source continues.

## 6. Data model

The final schema is:

`source, source_url, name_or_title, category, price, rating, author, tags, description, scraped_at`

Source-specific fields that do not apply are stored as empty/null values rather than invented data.

## 7. Cleaning

`processing/cleaning.py` contains pure transformation functions:

- whitespace and non-breaking-space cleanup
- quote-mark removal
- currency/number extraction for prices
- word-to-number rating conversion
- lowercase/sort/deduplicate tags
- URL normalization

## 8. Validation

Each cleaned record is checked for:

- recognized source
- required name/quote text
- valid HTTP/HTTPS URL
- non-negative numeric price when present
- rating from 1 to 5 when present
- author for quote records

Rejected records are logged and counted by reason.

## 9. Deduplication

Books use `source + normalized title`. Quotes use `source + normalized author + first 50 normalized characters of quote text`. Keys are lowercased, punctuation is removed, whitespace is collapsed, and the result is SHA-256 hashed.

The real practice websites are expected to contain unique records, but unit tests deliberately introduce duplicates to prove the logic works.

## 10. Error handling and logging

The shared HTTP client uses a `requests.Session`, a descriptive User-Agent, a 10-second timeout, and retries for transient HTTP statuses including 429, 500, 502, 503 and 504. Each request, page, rejection, and error is logged. A malformed individual record does not stop the source.

## 11. Tests

Run:

```bash
pytest -q
```

The tests cover cleaning, validation, URL handling, tag normalization, and duplicate detection without requiring internet access.

## 12. Output verification

After a successful run:

1. Check both source names appear in `final_dataset.csv`.
2. Confirm prices are numeric when present.
3. Confirm ratings are between 1 and 5 when present.
4. Confirm `final_record_count` matches the CSV row count.
5. Inspect `logs/scraper.log` for page progress and any warnings/errors.

## 13. Assumptions and limitations

- Category and description are left empty because the listing pages do not provide them and this implementation does not make approximately 1,000 additional book-detail requests.
- The quote `source_url` is the page on which the quote was collected; the author URL is extracted but is not part of the required final schema.
- The scraper respects a 0.5-second delay between requests.
- The pipeline does not bypass security controls or access restrictions.
- Internet availability can affect a live run.

## 14. Deployment

This project is primarily a batch/CLI assessment. A Docker image is included so the pipeline can run reproducibly on a container platform. See `Dockerfile` and `render.yaml`.

For a hosted batch deployment, create a Render Background Worker using this repository and the command:

```text
python main.py
```

The generated CSV/JSON/log files are runtime artifacts. For permanent hosted storage, add object storage or a database as a future enhancement.

## 15. AI usage

See `AI_USAGE.md`. AI assistance is disclosed and the final implementation should be reviewed, tested, and understood by the candidate.

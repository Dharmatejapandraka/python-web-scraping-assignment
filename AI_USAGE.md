# AI_USAGE.md

## Tool used

ChatGPT was used as a coding assistant.

## What AI was used for

- Interpreting the assessment requirements
- Planning the ETL pipeline and project structure
- Drafting scraping, cleaning, validation, deduplication, logging, and test code
- Reviewing edge cases and error handling
- Drafting documentation and deployment configuration

## Representative prompts

1. "Compare the assessment reference with the main assessment and identify every requirement."
2. "Build a Python Requests + BeautifulSoup scraper for Books to Scrape and Quotes to Scrape with dynamic pagination."
3. "Add cleaning, validation, duplicate detection, logging, tests, README, and summary JSON output."
4. "Prepare Docker and Render deployment configuration for this batch scraping project."

## AI-assisted areas

The initial implementation and documentation structure were AI-assisted. The candidate is responsible for reviewing the selectors, pipeline behavior, validation rules, output schema, and deployment configuration.

## Verification

The repository includes offline unit tests under `tests/`. Before submission, run `pytest -q` and then run `python main.py` from a clean virtual environment with internet access. Inspect the generated CSV, JSON summary, and log and reconcile the final row count with the summary.

## Important

AI output is not treated as automatically correct. The final code must be understood and explained by the candidate during the interview.

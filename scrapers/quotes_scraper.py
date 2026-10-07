"""Quotes to Scrape source scraper."""
from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    source_name = "Quotes to Scrape"

    def scrape(self) -> list[dict]:
        records: list[dict] = []
        url = BASE_URL
        page = 1

        while url:
            logger.info("Quotes page %d: %s", page, url)
            response = self.fetch(url)
            if response is None:
                logger.error("Stopping Quotes source after page failure: %s", url)
                break

            soup = BeautifulSoup(response.text, "lxml")
            for index, quote in enumerate(soup.select("div.quote"), start=1):
                try:
                    text = quote.select_one("span.text")
                    author = quote.select_one("small.author")
                    tags = quote.select("a.tag")
                    author_link = quote.select_one('a[href^="/author/"]')
                    if not text or not author:
                        raise ValueError("missing quote text/author")

                    records.append(
                        {
                            "source": self.source_name,
                            "source_url": url,
                            "name_or_title": text.get_text(" ", strip=True),
                            "category": None,
                            "price": None,
                            "rating": None,
                            "author": author.get_text(" ", strip=True),
                            "tags": [tag.get_text(" ", strip=True) for tag in tags],
                            "description": None,
                            "author_url": urljoin(url, author_link["href"]) if author_link and author_link.get("href") else None,
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Skipping quote record %d on page %d: %s", index, page, exc)

            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1

        logger.info("Quotes raw records collected: %d", len(records))
        return records

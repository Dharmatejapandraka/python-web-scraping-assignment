"""Books to Scrape source scraper."""
from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://books.toscrape.com/"


class BooksScraper(BaseScraper):
    source_name = "Books to Scrape"

    def scrape(self) -> list[dict]:
        records: list[dict] = []
        url = BASE_URL
        page = 1

        while url:
            logger.info("Books page %d: %s", page, url)

            response = self.fetch(url)
            if response is None:
                logger.error("Stopping Books source after page failure: %s", url)
                break

            soup = BeautifulSoup(response.text, "lxml")

            for index, article in enumerate(
                soup.select("article.product_pod"),
                start=1,
            ):
                try:
                    link = article.select_one("h3 > a")
                    price = article.select_one("p.price_color")
                    rating = article.select_one("p.star-rating")
                    availability = article.select_one(
                        "p.instock.availability"
                    )

                    if not link:
                        raise ValueError("missing book title/link")

                    book_url = urljoin(
                        url,
                        link.get("href", ""),
                    )

                    # Fetch the individual book detail page.
                    detail_response = self.fetch(book_url)

                    category = None
                    description = None

                    if detail_response is not None:
                        detail_soup = BeautifulSoup(
                            detail_response.text,
                            "lxml",
                        )

                        # Category is the third breadcrumb item:
                        # Home > Books > Category > Book title
                        breadcrumb_items = detail_soup.select(
                            "ul.breadcrumb li"
                        )

                        if len(breadcrumb_items) >= 3:
                            category = breadcrumb_items[2].get_text(
                                " ",
                                strip=True,
                            )

                        # Description is stored after:
                        # <div id="product_description">
                        description_heading = detail_soup.select_one(
                            "#product_description"
                        )

                        if description_heading:
                            description_element = (
                                description_heading.find_next_sibling("p")
                            )

                            if description_element:
                                description = description_element.get_text(
                                    " ",
                                    strip=True,
                                )

                    records.append(
                        {
                            "source": self.source_name,
                            "source_url": book_url,
                            "name_or_title": (
                                link.get("title")
                                or link.get_text(" ", strip=True)
                            ),
                            "category": category,
                            "price": (
                                price.get_text(" ", strip=True)
                                if price
                                else None
                            ),
                            "rating": (
                                " ".join(rating.get("class", []))
                                if rating
                                else None
                            ),
                            "author": None,
                            "tags": None,
                            "description": description,
                            "availability": (
                                availability.get_text(" ", strip=True)
                                if availability
                                else None
                            ),
                        }
                    )

                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "Skipping book record %d on page %d: %s",
                        index,
                        page,
                        exc,
                    )

            # Follow the website's actual next-page link.
            next_link = soup.select_one("li.next > a")

            url = (
                urljoin(url, next_link["href"])
                if next_link and next_link.get("href")
                else None
            )

            page += 1

        logger.info(
            "Books raw records collected: %d",
            len(records),
        )

        return records
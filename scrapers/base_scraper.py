"""Shared HTTP functionality for the scraping assignment."""
from __future__ import annotations

import logging
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    """Reusable HTTP client with retries, timeout and polite request delay."""

    def __init__(self, delay: float = 0.5, timeout: float = 10.0) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "Realiser-Technologies-Scraping-Assignment/1.0"}
        )
        retries = Retry(
            total=3,
            connect=3,
            read=3,
            status=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def fetch(self, url: str) -> Optional[requests.Response]:
        """Fetch a URL, returning None after a handled request failure."""
        try:
            logger.info("Request: %s", url)
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = "utf-8"
            return response
        except requests.RequestException as exc:
            logger.error("Request failed: %s | %s", url, exc)
            return None
        finally:
            time.sleep(self.delay)

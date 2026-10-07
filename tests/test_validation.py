from processing.validation import validate_record


def test_valid_book():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/a_1/index.html",
        "name_or_title": "A Book",
        "price": 10.5,
        "rating": 4,
    }
    assert validate_record(record) == []


def test_invalid_record_reports_reasons():
    record = {"source": "bad", "source_url": "x", "price": -1, "rating": 9}
    reasons = validate_record(record)
    assert "unknown_source" in reasons
    assert "missing_name_or_title" in reasons
    assert "invalid_url" in reasons
    assert "invalid_price" in reasons
    assert "invalid_rating" in reasons

"""Course catalog scraping and parsing."""

from .parser import parse_catalog
from .scraper import CatalogScraper

__all__ = ["CatalogScraper", "parse_catalog"]

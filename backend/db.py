"""Shared SQLite access for the API and the chatbot tools."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def image_url(image_file_path: str) -> str:
    # image_file_path is stored relative to data/, e.g. "products/basic-hoodie-big-yale.jpg"
    return f"/media/{image_file_path}"


def size_rank(size: str) -> int:
    return SIZE_ORDER.index(size) if size in SIZE_ORDER else len(SIZE_ORDER)


# Friendly shopping categories grouped from the catalogue's 22 raw garment types.
CATEGORIES = ["T-Shirts", "Long-Sleeve", "Hoodies", "Crewnecks", "Quarter-Zips", "Jackets & Fleece"]


def categorize(garment_type: str) -> str:
    """Map a raw garment_type to a shopper-facing category for filtering."""
    g = garment_type.lower()
    if "hood" in g:
        return "Hoodies"
    if "quarter-zip" in g or "1/4" in g or "quarter zip" in g:
        return "Quarter-Zips"
    if "jacket" in g or "fleece" in g:
        return "Jackets & Fleece"
    if "t-shirt" in g or "tee" in g or "t shirt" in g:
        return "T-Shirts"
    if "long-sleeve" in g or "long sleeve" in g:
        return "Long-Sleeve"
    if "crewneck" in g or "crew-neck" in g or "mockneck" in g or "sweatshirt" in g or "crewneck" in g:
        return "Crewnecks"
    return "Crewnecks"

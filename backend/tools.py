"""Chatbot tools: look up real product descriptions, prices and stock.

Every value these return comes straight from ``data/campus_customs.db``. The
agent must use them instead of guessing prices or quantities.
"""

import difflib
import json
import re

from db import SIZE_ORDER, get_db, size_rank
from models import ProductCard, ProductLookup, ProductSearchResult, SizeAvailability, SizeStock

# Treat similar words as the same, so "sweatshirt" finds hoodies and crewnecks,
# "sweater" finds fleece, "tee" finds t-shirts, and so on. Each key expands to a
# set of tokens that actually appear in the catalogue's names, types and tags.
SYNONYMS = {
    "hoodie": {"hoodie", "hooded", "sweatshirt", "pullover"},
    "hoody": {"hoodie", "hooded", "sweatshirt"},
    "hoodies": {"hoodie", "hooded", "sweatshirt", "pullover"},
    "sweatshirt": {"sweatshirt", "hoodie", "crewneck", "crew"},
    "sweater": {"sweater", "fleece", "crewneck", "sweatshirt"},
    "jumper": {"sweater", "sweatshirt", "hoodie", "crewneck"},
    "crewneck": {"crewneck", "crew", "sweatshirt"},
    "crew": {"crewneck", "crew"},
    "tee": {"tee", "shirt", "tshirt"},
    "tees": {"tee", "shirt", "tshirt"},
    "tshirt": {"tshirt", "shirt", "tee"},
    "shirt": {"shirt", "tee", "tshirt"},
    "jacket": {"jacket", "fleece", "bomber", "zip"},
    "fleece": {"fleece", "jacket", "sweater"},
    "quarterzip": {"quarter", "zip"},
    "zip": {"zip", "quarter"},
}

# Map the many ways a shopper might name a size to the catalogue's codes.
SIZE_SYNONYMS = {
    "xs": "XS", "extra small": "XS", "x small": "XS", "x-small": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x large": "XL", "x-large": "XL", "xlarge": "XL",
    "xxl": "XXL", "2xl": "XXL", "2x": "XXL", "xx large": "XXL", "xx-large": "XXL",
    "double xl": "XXL", "extra extra large": "XXL",
}

_STOPWORDS = {
    "a", "an", "the", "do", "you", "have", "has", "in", "on", "with", "for", "of",
    "me", "my", "i", "is", "are", "any", "some", "show", "get", "got", "this", "that",
    "it", "to", "and", "or", "whats", "what", "your", "there", "please", "want",
}


def normalize_size(size: str) -> str | None:
    """Turn a free-text size into a catalogue code (XS..XXL), or None."""
    key = size.strip().lower()
    if key.upper() in SIZE_ORDER:
        return key.upper()
    return SIZE_SYNONYMS.get(key)


def _tokens(*values: str) -> set[str]:
    joined = " ".join(values).lower()
    return set(re.findall(r"[a-z0-9]+", joined))


def _expand(terms: set[str]) -> set[str]:
    """Add synonyms so similar words (sweatshirt/hoodie) match the same items."""
    expanded = set(terms)
    for term in terms:
        expanded |= SYNONYMS.get(term, set())
    return expanded


def _term_hits(term: str, bag: set[str]) -> int:
    """2 for an exact token match, 1 for a close (typo-tolerant) match, else 0."""
    if term in bag:
        return 2
    if len(term) >= 4 and difflib.get_close_matches(term, bag, n=1, cutoff=0.82):
        return 1
    return 0


def _in_stock_sizes(conn) -> dict[str, list[str]]:
    """Map product_id -> sizes with quantity > 0, in XS..XXL order."""
    sizes: dict[str, list[str]] = {}
    for row in conn.execute("SELECT product_id, size FROM inventory WHERE quantity > 0"):
        sizes.setdefault(row["product_id"], []).append(row["size"])
    return {pid: sorted(s, key=size_rank) for pid, s in sizes.items()}


def search_catalogue(query: str, limit: int = 6) -> list[ProductSearchResult]:
    """Search the catalogue for products matching a shopper's words.

    Matches on name, garment type, description, colors and search tags. Returns
    the best matches with their real price and total stock. Empty list if none.
    """
    base_terms = {t for t in _tokens(query) if t not in _STOPWORDS}
    query_terms = _expand(base_terms)
    results: list[tuple[int, ProductSearchResult]] = []

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            """
        ).fetchall()
        sizes_by_product = _in_stock_sizes(conn)

    for row in rows:
        colors = json.loads(row["colors"])
        tags = json.loads(row["search_tags"])
        bag = _tokens(row["name"], row["garment_type"], row["description"], " ".join(colors), " ".join(tags))
        # Name/type/tags count double vs. description-only matches.
        name_bag = _tokens(row["name"], row["garment_type"], " ".join(tags))
        score = 0
        if query_terms:
            score = sum(_term_hits(term, bag) + _term_hits(term, name_bag) for term in query_terms)
        if score > 0:
            results.append(
                (
                    score,
                    ProductSearchResult(
                        product_id=row["product_id"],
                        name=row["name"],
                        garment_type=row["garment_type"],
                        price=row["price"],
                        colors=colors,
                        total_stock=row["total_stock"],
                        in_stock=row["total_stock"] > 0,
                        in_stock_sizes=sizes_by_product.get(row["product_id"], []),
                    ),
                )
            )

    results.sort(key=lambda pair: (pair[0], pair[1].total_stock), reverse=True)
    return [result for _, result in results[: max(1, min(limit, 12))]]


def get_product_details(product_id: str) -> ProductLookup:
    """Full details for one product: description, price, colors and per-size stock.

    Use this for questions about a product's price, description or stock.
    """
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return ProductLookup(found=False, message=f"No product found with id '{product_id}'.")
        stock_rows = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    inventory = sorted(
        (SizeStock(size=s["size"], quantity=s["quantity"]) for s in stock_rows),
        key=lambda s: size_rank(s.size),
    )
    card = ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        image_url=f"/media/{row['image_file_path']}",
        inventory=inventory,
        total_stock=sum(s.quantity for s in inventory),
    )
    return ProductLookup(found=True, message="Found.", product=card)


def check_size_stock(product_id: str, size: str) -> SizeAvailability:
    """Check real stock for one specific size of one product.

    Use this when a shopper asks about a size. Clearly reports out-of-stock
    sizes. Never guess a quantity; this reads the inventory table directly.
    """
    normalized = normalize_size(size)

    with get_db() as conn:
        product = conn.execute(
            "SELECT product_id, name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if product is None:
            return SizeAvailability(
                product_id=product_id,
                product_name="",
                size=size,
                available=False,
                quantity=0,
                status=f"No product found with id '{product_id}'.",
            )

        if normalized is None:
            sizes = _in_stock_sizes(conn).get(product_id, [])
            return SizeAvailability(
                product_id=product_id,
                product_name=product["name"],
                size=size,
                available=False,
                quantity=0,
                status=f"'{size}' isn't a size we carry. Sizes are XS, S, M, L, XL and XXL.",
                in_stock_sizes=sizes,
            )

        row = conn.execute(
            "SELECT quantity FROM inventory WHERE product_id = ? AND size = ?",
            (product_id, normalized),
        ).fetchone()
        in_stock_sizes = _in_stock_sizes(conn).get(product_id, [])

    quantity = row["quantity"] if row is not None else 0
    available = quantity > 0
    if not available:
        status = f"Out of stock in {normalized}."
    elif quantity <= 5:
        status = f"In stock in {normalized}, only {quantity} left."
    else:
        status = f"In stock in {normalized} ({quantity} available)."

    return SizeAvailability(
        product_id=product_id,
        product_name=product["name"],
        size=normalized,
        available=available,
        quantity=quantity,
        status=status,
        in_stock_sizes=[s for s in in_stock_sizes if s != normalized],
    )

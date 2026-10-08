"""Persist and load chat history for logged-in shoppers.

History is stored in the ``chat_messages`` table, linked to ``users.id``. Each
assistant turn also stores the product cards it showed (as JSON) so they can be
redrawn when the conversation is reloaded.
"""

import json

from db import get_db
from models import ChatHistory, ChatHistoryMessage, ProductCard

HISTORY_LIMIT = 100


def user_exists(user_id: int) -> bool:
    with get_db() as conn:
        return conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone() is not None


def save_turn(user_id: int, user_message: str, assistant_message: str, products: list[ProductCard]) -> None:
    """Save one user message and the assistant's reply (with its product cards)."""
    products_json = json.dumps([p.model_dump() for p in products]) if products else None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'user', ?, NULL)",
            (user_id, user_message),
        )
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, assistant_message, products_json),
        )
        conn.commit()


def load_history(user_id: int) -> ChatHistory:
    """Load a shopper's saved messages, oldest first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id LIMIT ?",
            (user_id, HISTORY_LIMIT),
        ).fetchall()

    messages: list[ChatHistoryMessage] = []
    for row in rows:
        products: list[ProductCard] = []
        if row["products_json"]:
            try:
                products = [ProductCard.model_validate(p) for p in json.loads(row["products_json"])]
            except (ValueError, TypeError):
                products = []  # tolerate old rows in a different shape
        messages.append(ChatHistoryMessage(role=row["role"], content=row["content"], products=products))
    return ChatHistory(messages=messages)

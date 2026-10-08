import json
import logging
import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent import run_chat
from auth import hash_password, verify_password
from chat_store import load_history, save_turn, user_exists
from db import PRODUCTS_DIR, categorize, get_db, image_url, size_rank
from models import (
    ChatHistory,
    ChatRequest,
    ChatResponse,
    LoginRequest,
    ProductDetail,
    ProductSummary,
    PublicUser,
    ResetPasswordRequest,
    SignupRequest,
    SizeStock,
)

logger = logging.getLogger("campus_customs")

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Only the products folder is public. Mounting all of data/ would expose the database file.
app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="product-images")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """One chat turn: the agent's reply plus real product cards to render.

    For a signed-in shopper (valid user_id), the turn is saved to their history.
    """
    try:
        response = await run_chat(body)
    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(status_code=502, detail="The assistant is having trouble right now. Please try again.")

    if body.user_id is not None and user_exists(body.user_id):
        try:
            save_turn(body.user_id, body.message, response.message, response.products)
        except Exception:
            logger.exception("Failed to save chat turn for user %s", body.user_id)

    return response


@app.get("/api/chat/history", response_model=ChatHistory)
def chat_history(user_id: int) -> ChatHistory:
    """Load a signed-in shopper's saved conversation so it's there when they return."""
    if not user_exists(user_id):
        raise HTTPException(status_code=404, detail="No such user.")
    return load_history(user_id)


def public_user(row: sqlite3.Row) -> PublicUser:
    # Never expose password_hash to the client.
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


@app.post("/api/signup", response_model=PublicUser, status_code=201)
def signup(body: SignupRequest) -> PublicUser:
    first = body.first_name.strip()
    last = body.last_name.strip()
    email = body.email.strip().lower()
    full_name = f"{first} {last}"
    password_hash = hash_password(body.password)

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, password_hash, first, last),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()

    return public_user(row)


@app.post("/api/login", response_model=PublicUser)
def login(body: LoginRequest) -> PublicUser:
    email = body.email.strip().lower()
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    # Same error whether the email is unknown or the password is wrong, so we
    # don't reveal which accounts exist.
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    return public_user(row)


@app.post("/api/reset-password", response_model=PublicUser)
def reset_password(body: ResetPasswordRequest) -> PublicUser:
    """Set a new password for an existing account.

    This lets a user (for example a seed account whose original password is
    unknown) choose a fresh password. It only ever writes a new hash from the
    supplied plaintext; it never reads or guesses the old password.

    NOTE: for coursework this trusts whoever submits the email. A production
    reset would require an emailed, single-use token to prove ownership.
    """
    email = body.email.strip().lower()
    new_hash = hash_password(body.new_password)

    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="No account with this email.")
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, row["id"]))
        conn.commit()
        updated = conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()

    return public_user(updated)


@app.get("/api/products", response_model=list[ProductSummary])
def list_products() -> list[ProductSummary]:
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
            FROM catalogue c
            LEFT JOIN inventory i ON i.product_id = c.product_id
            GROUP BY c.product_id
            ORDER BY c.name
            """
        ).fetchall()

    return [
        ProductSummary(
            product_id=row["product_id"],
            name=row["name"],
            garment_type=row["garment_type"],
            category=categorize(row["garment_type"]),
            description=row["description"],
            colors=json.loads(row["colors"]),
            price=row["price"],
            image_url=image_url(row["image_file_path"]),
            total_stock=row["total_stock"],
        )
        for row in rows
    ]


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock_rows = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    inventory = sorted(
        (SizeStock(size=s["size"], quantity=s["quantity"]) for s in stock_rows),
        key=lambda s: size_rank(s.size),
    )

    return ProductDetail(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        category=categorize(row["garment_type"]),
        description=row["description"],
        colors=json.loads(row["colors"]),
        search_tags=json.loads(row["search_tags"]),
        price=row["price"],
        image_url=image_url(row["image_file_path"]),
        total_stock=sum(s.quantity for s in inventory),
        inventory=inventory,
    )

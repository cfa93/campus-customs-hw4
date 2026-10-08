"""Shared Pydantic types for the Campus Customs API and chatbot.

These are the structured shapes passed between the database, the FastAPI
endpoints, the PydanticAI agent and the React frontend.
"""

from typing import Literal

from pydantic import BaseModel, EmailStr, Field

# --- Products -------------------------------------------------------------


class SizeStock(BaseModel):
    """Stock for one size of one product."""

    size: str
    quantity: int


class ProductSummary(BaseModel):
    """A product as shown in the Products grid."""

    product_id: str
    name: str
    garment_type: str
    category: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    total_stock: int


class ProductDetail(ProductSummary):
    """A product as shown on its own page: adds tags and per-size stock."""

    search_tags: list[str]
    inventory: list[SizeStock]


class ProductCard(BaseModel):
    """A product the chatbot chose to show in the chat product panel.

    Hydrated from the database by the backend (not written by the model), so
    stock and price are always real.
    """

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    inventory: list[SizeStock]
    total_stock: int


# --- Chat -----------------------------------------------------------------


class ChatReply(BaseModel):
    """Structured output the agent returns.

    The model writes the reply text and names which products to display by id.
    The backend turns those ids into real ProductCards, so the model can't
    invent prices or stock.
    """

    message: str = Field(description="The assistant's reply to the shopper, in light Markdown.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values of catalogue items to show as cards, in display order. Empty if none.",
    )


# --- Tool results ---------------------------------------------------------
# Field descriptions are sent to the model as part of the tool schema.


class ProductSearchResult(BaseModel):
    """A catalogue match returned by search_catalogue."""

    product_id: str = Field(description="Id to pass to other tools and to put in product_ids.")
    name: str = Field(description="Display name to use when talking to the shopper.")
    garment_type: str = Field(description="Kind of item, e.g. 'pullover hoodie'.")
    price: float = Field(description="Price in US dollars, exactly as stored.")
    colors: list[str] = Field(description="Colors this product comes in.")
    total_stock: int = Field(description="Units in stock across all sizes.")
    in_stock: bool = Field(description="False if every size is sold out.")
    in_stock_sizes: list[str] = Field(description="Sizes with at least one unit, in XS..XXL order.")


class ProductLookup(BaseModel):
    """Result of get_product_details: the product, or a clear not-found."""

    found: bool = Field(description="False if no product has this id.")
    message: str = Field(description="Short status, e.g. why nothing was found.")
    product: ProductCard | None = Field(
        default=None, description="Full product with description, price, colors and per-size stock."
    )


class SizeAvailability(BaseModel):
    """Stock for one specific size of one product, from check_size_stock."""

    product_id: str = Field(description="The product that was checked.")
    product_name: str = Field(description="Display name, empty if the product wasn't found.")
    size: str = Field(description="Normalized size code (XS..XXL), or the shopper's text if not recognized.")
    available: bool = Field(description="True only if quantity is above 0.")
    quantity: int = Field(description="Exact units in stock for this size.")
    status: str = Field(description="Plain-English summary to relay, e.g. 'Out of stock in M.'")
    in_stock_sizes: list[str] = Field(
        default_factory=list, description="Other sizes of this product that are in stock, for suggestions."
    )


class ChatTurn(BaseModel):
    """One earlier message in the conversation, sent back for context."""

    role: Literal["user", "assistant"]
    content: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    """A chat turn sent from the frontend."""

    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list, max_length=20)
    # Who's chatting (null for a guest). Passed to the agent so it can greet them
    # and used to save/load their history.
    user_id: int | None = None
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=320)
    # The product the shopper is currently looking at, so "this" / "it" resolves.
    current_product_id: str | None = Field(default=None, max_length=200)


class ChatHistoryMessage(BaseModel):
    """One saved message, returned when a shopper's history loads."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class ChatHistory(BaseModel):
    """A logged-in shopper's saved conversation."""

    messages: list[ChatHistoryMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """What the frontend receives for one chat turn: reply text + real cards."""

    message: str
    products: list[ProductCard] = Field(default_factory=list)


# --- Auth -----------------------------------------------------------------


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str = Field(min_length=8, max_length=200)


class PublicUser(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    name: str
    email: str

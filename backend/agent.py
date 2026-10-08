"""Campus Customs chatbot agent configuration.

Builds a PydanticAI agent that:
- loads its system prompt from ``prompts/prompt.md`` (tone + safety rules), and
- talks to the course model ``gpt-5.6-luna`` through the Portkey gateway,
  authenticated with ``PORTKEY_API_KEY`` from the root ``.env`` file.

The chat endpoint and catalogue tools are wired up in a later step; this module
owns the prompt loading and model/agent setup.
"""

from __future__ import annotations

import functools
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart

from audit import append_audit_entry
from models import ChatReply, ChatRequest, ChatResponse, ProductCard
from tools import check_size_stock, get_product_details, search_catalogue

# Result caps and loop limits.
MAX_CARDS = 8  # most product cards returned to the page per reply
REQUEST_LIMIT = 6  # most model requests (loop rounds) per chat turn
TOOL_CALLS_LIMIT = 10  # most tool calls per chat turn
USAGE_LIMITS = UsageLimits(request_limit=REQUEST_LIMIT, tool_calls_limit=TOOL_CALLS_LIMIT)


def _summarize(result: object) -> str:
    """Short, human-readable summary of a tool result for the audit log."""
    if isinstance(result, list):
        ids = [getattr(r, "product_id", "") for r in result]
        return f"{len(result)} result(s): {[i for i in ids if i][:6]}"
    if hasattr(result, "status"):
        return str(result.status)
    if hasattr(result, "found"):
        name = getattr(getattr(result, "product", None), "name", None)
        return f"found={result.found}" + (f" ({name})" if name else "")
    return str(result)[:120]


def _audited(func):
    """Wrap a tool so each call is recorded in the audit trail."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logged_args = {**{f"arg{i}": a for i, a in enumerate(args)}, **kwargs}
        append_audit_entry(func.__name__, logged_args, _summarize(result))
        return result

    return wrapper


@dataclass
class ChatDeps:
    """Per-conversation context handed to the agent on each run."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    # The product the shopper is viewing right now, if any (resolves "this"/"it").
    current_product_id: str | None = None
    current_product_name: str | None = None

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.md"
# Look for the .env in the hw4 repo root first (where graders put it), then fall
# back to the parent course folder used during development.
ENV_CANDIDATES = [
    Path(__file__).resolve().parent.parent / ".env",
    Path(__file__).resolve().parents[2] / ".env",
]

# AGENTS.md: use OpenAI via Portkey with the gpt-5.6-luna model.
MODEL_NAME = os.getenv("CAMPUS_CUSTOMS_MODEL", "gpt-5.6-luna")


def load_system_prompt() -> str:
    """Read the shared tone + safety prompt from disk."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def _create_client() -> AsyncOpenAI:
    """OpenAI-compatible client routed through Portkey (same setup as hw3)."""
    for env_path in ENV_CANDIDATES:
        if env_path.exists():
            load_dotenv(env_path)
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set (expected in the root .env file).")
    return AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        default_headers={"x-portkey-provider": os.getenv("PORTKEY_PROVIDER", "openai")},
    )


def build_model() -> OpenAIChatModel:
    """Configure the PydanticAI model for gpt-5.6-luna via Portkey."""
    return OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=_create_client()))


@lru_cache(maxsize=1)
def get_agent() -> Agent[ChatDeps, ChatReply]:
    """Build (once) the Campus Customs agent with structured ChatReply output
    and the catalogue tools for descriptions, prices and stock."""
    agent = Agent(
        build_model(),
        deps_type=ChatDeps,
        output_type=ChatReply,
        system_prompt=load_system_prompt(),
    )
    # Tools read live data from campus_customs.db, so the model never invents
    # prices or quantities.
    agent.tool_plain(_audited(search_catalogue))
    agent.tool_plain(_audited(get_product_details))
    agent.tool_plain(_audited(check_size_stock))

    @agent.system_prompt
    def who_is_chatting(ctx: RunContext[ChatDeps]) -> str:
        deps = ctx.deps
        if not deps.first_name and not deps.email:
            return "The shopper is a guest (not signed in). Don't assume a name."
        name = " ".join(p for p in [deps.first_name, deps.last_name] if p) or "there"
        email = f" ({deps.email})" if deps.email else ""
        return f"The signed-in shopper is {name}{email}. Greet them by their first name naturally."

    @agent.system_prompt
    def current_page(ctx: RunContext[ChatDeps]) -> str:
        deps = ctx.deps
        if not deps.current_product_id:
            return ""
        label = deps.current_product_name or deps.current_product_id
        return (
            f"The shopper is currently viewing this product page: {label} "
            f"(product_id: {deps.current_product_id}). If they say 'this', 'it', 'this one' or "
            f"ask about the item on the page, they mean this product. Use this product_id with your "
            f"tools (for example to check a color or a size) unless they clearly mean something else."
        )

    return agent


def _to_history(request: ChatRequest) -> list[ModelMessage]:
    """Turn the frontend's recent turns into PydanticAI message history."""
    history: list[ModelMessage] = []
    for turn in request.history:
        if turn.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            history.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return history


def _hydrate_cards(product_ids: list[str]) -> list[ProductCard]:
    """Build real product cards from the ids the model chose.

    Unknown ids are dropped and duplicates removed, so a made-up id can never
    reach the page. Prices and stock come from the database, not the model.
    """
    cards: list[ProductCard] = []
    seen: set[str] = set()
    for product_id in product_ids:
        if product_id in seen:
            continue
        seen.add(product_id)
        lookup = get_product_details(product_id)
        if lookup.found and lookup.product is not None:
            cards.append(lookup.product)
        if len(cards) >= MAX_CARDS:
            break
    return cards


def _build_deps(request: ChatRequest) -> ChatDeps:
    """Assemble the agent's per-run context, resolving the current product name."""
    current_name: str | None = None
    if request.current_product_id:
        lookup = get_product_details(request.current_product_id)
        if lookup.found and lookup.product is not None:
            current_name = lookup.product.name
    return ChatDeps(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        current_product_id=request.current_product_id if current_name else None,
        current_product_name=current_name,
    )


async def run_chat(request: ChatRequest) -> ChatResponse:
    """Answer one chat turn and attach the matching product cards."""
    who = request.first_name or "guest"
    append_audit_entry("agent", {"message": request.message[:120], "user": who}, "run started")
    try:
        result = await get_agent().run(
            request.message,
            deps=_build_deps(request),
            message_history=_to_history(request),
            usage_limits=USAGE_LIMITS,
        )
    except Exception as exc:
        append_audit_entry("agent", {"message": request.message[:120]}, f"error: {type(exc).__name__}", stop_reason="error")
        raise

    reply = result.output
    response = ChatResponse(message=reply.message, products=_hydrate_cards(reply.product_ids))
    append_audit_entry(
        "agent",
        {"products": len(response.products)},
        reply.message[:150],
        stop_reason="completed",
    )
    return response


if __name__ == "__main__":
    # Smoke check that doesn't need the API key: prompt loads and model name is set.
    prompt = load_system_prompt()
    print(f"Model: {MODEL_NAME}")
    print(f"Prompt loaded: {len(prompt)} chars from {PROMPT_PATH.name}")

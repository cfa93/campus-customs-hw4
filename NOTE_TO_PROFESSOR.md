# Campus Customs — Note to the Professor

**Student:** Nijat Hasanli (nijat.hasanli@yale.edu)
**Project:** Campus Customs — a Yale merch shop with an AI shopping assistant.

Dear Professor Zaman,

This is my hw4 submission: a small e-commerce site for a Yale merch store, with a
chatbot that helps shoppers find products using the real catalogue. It's built as a
React + Vite + TypeScript frontend and a Python FastAPI + PydanticAI backend over the
provided `data/campus_customs.db`.

## What it does

- **Storefront:** Home, Products, About, Log in and Create account pages, with a navy
  Yale-merch look. The Products page has category and price filters.
- **Product pages:** each product opens its own page with a large photo and full
  description, price, and per-size stock read from the database.
- **Accounts:** sign up and log in with passwords hashed using PBKDF2-SHA256 (no
  plain-text passwords stored), plus a password-reset flow.
- **Chatbot:** a floating assistant (model `gpt-5.6-luna` via Portkey) that searches
  the catalogue and answers questions about descriptions, prices and stock. It uses
  tools that read the database directly, so it never invents prices or quantities, and
  it clearly reports when a size is out of stock. Matching products appear as clickable
  cards that open the same product pages.
- **Context aware:** the bot knows the signed-in shopper's name and the product page
  they're viewing, so "do you have this in pink?" resolves to the right item. It asks a
  follow-up question when a request is ambiguous instead of guessing.
- **Saved history:** logged-in shoppers' conversations are saved and reloaded on their
  next visit; guests can chat too, but aren't saved.

## How to run it

1. **Backend** (needs `PORTKEY_API_KEY` in the root `.env`):
   ```
   cd backend
   python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
   .venv/Scripts/python -m uvicorn main:app --reload --port 8000
   ```
2. **Frontend:**
   ```
   cd frontend
   npm install
   npm run dev
   ```
   Then open http://localhost:5173 (the dev server proxies the API and images to the
   backend).

## Where to look

- `AI_prompts.md` — the prompts I sent, one section per problem.
- `output/harness.md` — how everything works (database, API, agent, tools, history).
- `output/usability.md` — the four usability improvements and why each helps.
- `output/design.md` — the visual design choices and their shopper/business rationale.

## A note on the data

The repository is public, so `data/campus_customs.db` and `data/products/` are
git-ignored and not committed, and the Portkey API key is only read from `.env` and is
never printed or committed.

Thank you for taking a look.

— Nijat

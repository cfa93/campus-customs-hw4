# Campus Customs

A Yale campus-merch shop with an AI shopping assistant.

- **Frontend:** React + Vite + TypeScript (`frontend/`)
- **Backend:** Python + FastAPI + PydanticAI (`backend/`)
- **Chatbot model:** `gpt-5.6-luna` via the Portkey gateway
- The assistant answers questions about products, prices, sizes and stock, reading
  everything live from the SQLite database so it never invents a price or quantity.

## 1. Add the local data pack

The database and product images are **not** in git. Put the provided data pack in a
`data/` folder at the repo root so the layout is:

```
data/
  campus_customs.db
  products/
    <product images>.jpg
```

(The backend expects `data/campus_customs.db` and serves images from `data/products/`.)

## 2. Set your API key

Copy the example env file to `.env` in the repo root and add your Portkey key:

```
cp .env.example .env
# then edit .env and set PORTKEY_API_KEY=...
```

`.env` is git-ignored and must never be committed.

## 3. Run the backend

From the repo root (Python 3.11+):

```
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt

cd backend
uvicorn main:app --reload --port 8000
```

The API runs on http://127.0.0.1:8000. It must be started from the `backend/` folder
so its modules import correctly.

## 4. Run the frontend

In a second terminal (Node 18+):

```
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` and `/media` to the
backend on port 8000, so start the backend first.

## Project layout

```
hw4/
  AI_prompts.md            # every prompt sent, by problem
  requirements.txt         # Python dependencies
  .env.example             # copy to .env and add your key
  .gitignore
  README.md
  frontend/                # React + Vite + TypeScript app
  backend/
    main.py                # FastAPI app and routes
    agent.py               # PydanticAI agent: model, prompt, tools, loop limits
    models.py              # shared Pydantic types
    tools.py               # catalogue search + price/stock lookups
    auth.py                # password hashing
    db.py                  # shared SQLite access
    chat_store.py          # saved chat history
    audit.py               # append-only audit trail
    prompts/
      prompt.md            # chatbot tone + safety rules
  output/
    harness.md             # how everything works
    design.md              # visual design notes
    usability.md           # usability improvements
    app_check.html         # live app checks with screenshots
    app_check_images/      # screenshots used by app_check.html
    audit_trail.json       # logged agent activity
```

`data/` (the database and product images) and `.env` live outside version control.

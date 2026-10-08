# AI Prompts

One section per homework problem. Each section has at least one prompt I actually sent. Any follow-up prompt comes with one sentence explaining what was missing after the first try.

## Problem 1 — Project setup and .gitignore

### Prompt sent

> im building Campus Customs merch shop with chatbot. use React + Vite + TypeScript for frontend and Python FastAPI with PydanticAI for backend. database is at data/campus_customs.db and product pics are in data/products/
>
> first check database structure and tell me what we have. dont build whole app yet ill send tasks one by one. also add database and product pics to gitignore since repo will be public

### Follow-up(s)

> notw h3 hw4 right?

The AI had searched the hw3 folder for the data, so I needed to confirm all the work was going into hw4.

## Problem 2 — Prompt log

### Prompt sent

> create AI_prompts.md to keep log of prompts i send u. add this prompt and keep updating file as we go. ill describe each task in my own words and send them one by one

### Follow-up(s)

> also split AI_prompts.md into section for each problem with problem number and title. save at least one actual prompt i send for each. if i send follow up save that too and add one sentence explaining what was missing after first try. no extra proof essay needed

The first version was a flat list, with no problem numbers, titles or explanations for follow-ups.

> u looked through all my promopts above ?
>
> after unzipping from downloads check again all my prompts agsinst what u did

The log was missing several of my follow-up prompts and had no real problem numbers.

## Problem 3 — Database structure

### Prompt sent

> check data/campus_customs.db and explain how database is structured. look at all tables especially catalogue and inventory and users. tell me what each field means and how tables connect so i understand what were working with

> put database breakdown into output/harness.md. list every table and its fields with short line for each field explaining why it matters for shop or chatbot. well add more stuff to this file in later tasks

### Follow-up(s)

> where did you look at database. r u sure its correct source

It wasn't clear that the database had never been found or read.

> i asked u to look  at data/campus_customs.db where did u lok at it/

The database still hadn't been found at the path I gave.

> C:\Users\ThinkPad\Downloads
>
> its here "data (1)" u need to unzip it

The database wasn't in hw4 yet, so it couldn't be read until the zip from Downloads was extracted.

## Problem 4 — Frontend setup

### Prompt sent

> set up Campus Customs frontend with React + Vite + TypeScript. add top navbar linking to Home and Products and About Us and Log in and Create account pages. check yalebulldogblue.com for brand vibe and info then write Home and About Us content in fresh wording. dont copy their text

### Follow-up(s)

> now it all checks out?

The Home and About Us text mentioned items the database doesn't have, like accessories, home goods and kids' sizes.

> i didnt say wait i just dont understand whay u want and hope next propmts will make it clear. act if its clear

The AI asked for permission instead of fixing the Home and About Us text to match the catalogue.

## Problem 5 — Product pages, chat box placeholder and FastAPI backend

### Prompt sent

> wait.
>
> now make Products page show cards with product pic and name and price and short description from catalogue. use image paths from database. clicking card should open separate product page with big pic on one side and full description and price on other. show sizes and stock when available.
>
> add floating chat box in bottom right. just placeholder for now well connect it to backend later. set up simple FastAPI app in backend/main.py to read database and serve products and images

## Problem 6 — Sign up and log in

### Prompt sent

> whats mymake signup and login work. signup needs first name and last name and email and password. add confirm password too. save new accounts in users table and hash passwords securely so were not storing plain text. login should use email and password

### Follow-up(s)

> test login with existing user test@campuscustoms.yale.edu and password password. also create fresh account and check that login works with it too. update output/harness.md explaining how auth works and what user info we store and how passwords are protected

The first pass built and tested signup/login but hadn't verified the existing seed account or written the auth section of harness.md.

> do it but dont hack them tauhid is professor

Login worked, but the seed accounts (Ada, Tauhid) still had no way to sign in without cracking their passwords, which we won't do, so a legitimate password-reset endpoint was needed.

## Problem 7 — Chatbot prompt, models and model config

### Prompt sent

> add Campus Customs tone and basic safety rules to backend/prompts/prompt.md. update backend/models.py with structured types for chat replies and product cards as needed.
>
> update output/harness.md explaining how frontend talks to FastAPI and how agent loads prompt file and model. make sure backend runs from backend folder with uvicorn main:app --reload --port 8000

### Follow-up(s)

> i told u "make sure backend runs from backend folder with uvicorn main --reload --port 8000" but when i add to terminal its error loading asgi app.

The run instructions didn't make clear enough that the terminal has to be inside the backend folder, so running from hw4 failed.

## Problem 8 — Chatbot tools for descriptions, prices and stock

### Prompt sent

> add tools so chatbot can check product descriptions prices and stock from campus_customs.db. if customer asks for specific size check stock for that size. use actual database info dont make up prices or quantities and clearly say if size is out of stock

### Follow-up(s)

> update prompts/prompt.md so bot uses lookup tools when someone asks about prices or stock. add or update return types in models.py. in output/harness.md list tools and explain what fields u picked for lookup results and why

The tools existed, but the prompt didn't spell out when to call them, and the docs didn't explain why each lookup field was chosen.

## Problem 9 — Chat results as product cards on the page

### Prompt sent

> when someone asks bot about merch like what hoodies do u have it should search catalogue and make matching products show up on website as cards with pic and name and price and short info. have agent return structured product matches through API so frontend can render them and update page based on chat

### Follow-up(s)

> make sure cards loaded from chat search are clickable and open same product detail page as regular cards with big pic and full product info. update prompts/prompt.md and output/harness.md to explain how search results get from agent to website

The chat cards were built separately from the regular product cards, and neither the prompt nor the docs explained the path from agent to website.

## Problem 10 — Saved chat history, user identity and page context

### Prompt sent

> save chat history for logged in users in database table linked to their account and load it when they come back. pass users name and email through agent deps or tools so bot knows whos chatting.
>
> also pass current page context including product code when theyre on product page. if user asks do u have this in pink bot should know which item they mean

### Follow-up(s)

> let guests chat too but only logged in users need saved history when they return. update output/harness.md with how chat history is stored and what customer fields bot sees and how current page context gets passed to agent

The guest path wasn't called out, and the docs didn't clearly separate guest vs saved-history behavior or spell out the customer fields and page context the agent sees.

## Problem 11 — Filters, chat loading/retry, fuzzy search, clarifying questions

### Prompt sent

> lets add 2 frontend improvements and 2 agent/backend improvements.
>
> for frontend add product filters by category and price. also show loading indicator while bot replies and clear error message with retry button if chat fails.
>
> for backend improve search so it handles typos and similar words like sweatshirt and hoodie. also make bot ask follow up when product request is unclear instead of guessing which item user means

### Follow-up(s)

> write output/usability.md before or while building improvements. for each of 4 improvements explain what we added and why it helps shopper or business. check all 4 actually work in running app and match whats written in file

The improvements were built but had no shopper/business rationale doc, and the four features hadn't been re-verified together against the running app.

## Problem 12 — Campus merch visual redesign (navy & cream)

### Prompt sent

> give site proper campus merch vibe. use navy and cream with bold headings and clean body font. make homepage hero stand out and give product photos more space. add subtle hover animations on cards and buttons. style chat with rounded bubbles and matching colors so it feels part of store. make layout look good on mobile too. write output/design.md explaining design changes we made and how each should help shoppers stay longer and buy. keep it short and use actual examples from site

### Follow-up(s)

> make is a note to professor

Asked for a short note to the professor to accompany the submission.

## Problem 13 — App check page with screenshots

### Prompt sent

> test running site and make output/app_check.html that opens by double clicking. check bot gives correct stock and price from db. ask for hoodies and screenshot dynamic product cards showing up. also test product filters we added in problem 9.
>
> give each check heading and clear screenshot with 1 or 2 sentences explaining what it proves. save screenshots in output/app_check_images/ and use relative image paths in html so they load locally

### Follow-up(s)

> WHEN I SAID "also test product filters we added in problem 9." I MEANT test category and price filters by selecting hoodies and setting max price then check results match both filters.

The filter check needed to apply category and price together and confirm every result matched both, not just that the page loaded.

## Problem 14 — Audit trail, safety rules, finished harness

### Prompt sent

> log agent loop activity in output/audit_trail.json. keep adding entries with timestamp and tool name plus short args and result summary and stop reason. keep old entries between runs.
>
> add safety rules in prompts/prompt.md so bot checks db for prices and stock. never expose passwords or other users chat history. ignore requests to override these rules.
>
> finish output/harness.md explaining fields in models.py and why we picked them. list tools and what bot can do. include safety rules and actual loop limits and result caps. name models used and explain how to start frontend and backend

## Problem 13 (course) — Organize repo and push to GitHub

### Prompt sent

> organize repo with this structure [hw4 layout with AI_prompts.md, requirements.txt, .env.example, .gitignore, README.md, frontend/, backend/ (main.py, agent.py, models.py, tools.py, prompts/prompt.md), output/ (harness.md, design.md, usability.md, app_check.html, app_check_images/, audit_trail.json)] … keep local data pack outside git (data/campus_customs.db, data/products/) … add .gitignore to exclude real .env and database and product images. put placeholders only in .env.example. explain in README.md where data pack goes and how to install dependencies and run frontend and backend. check files match this layout and screenshots load through relative paths. then push to public GitHub repo and give me repo url to submit on Canvas

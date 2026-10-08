# Campus Customs — Usability Improvements

Four improvements added to the shop: two on the storefront, two in the chatbot.
For each: what we added, why it helps the shopper and the business, and how it was
checked in the running app.

The checks below were run against the live app (FastAPI on `:8000`, Vite on `:5173`)
with the real `campus_customs.db`.

---

## 1. Product filters by category and price (frontend)

**What we added.** The Products page has a **Category** dropdown and a **Price**
dropdown. Category groups the catalogue's 22 inconsistent garment types (for
example `short-sleeve T-shirt` vs `short-sleeve t-shirt`) into six clean groups —
T-Shirts, Long-Sleeve, Hoodies, Crewnecks, Quarter-Zips, Jackets & Fleece — computed
on the backend so the labels are consistent. Price has simple bands (Under $40,
$40–60, $60–80, $80+). The page shows a live "Showing N of M" count and a Clear
filters button.

**Why it helps the shopper.** With 102 products on one page, filters let a shopper
jump straight to what they want ("hoodies under $60") instead of scrolling the whole
grid. The plain price bands match how people actually shop to a budget.

**Why it helps the business.** Shoppers who find things fast buy more and leave less
often. Grouping messy garment types into clean categories also means the catalogue
can grow without the storefront looking disorganized.

**Verified in the app.** `/api/products` returns a `category` for every product
(T-Shirts 25, Crewnecks 29, Hoodies 27, Quarter-Zips 11, Jackets & Fleece 8,
Long-Sleeve 2 = 102). Applying the page's filter logic to the live data gives correct
subsets — e.g. Hoodies at $60–80 → 23 products, T-Shirts under $40 → 25.

---

## 2. Chat loading indicator and error with retry (frontend)

**What we added.** While the assistant is answering, the chat shows a "Looking that
up" bubble with animated dots. If a turn fails, the chat shows a clear "Couldn't
reach the shop" message with a **Retry** button that resends the same question (with
the same conversation context); the shopper's message stays on screen.

**Why it helps the shopper.** The shopper can see the bot is working rather than
wondering if the app froze, and a failed message isn't a dead end — one tap retries
it, with no retyping.

**Why it helps the business.** A visible "working" state and an easy recovery keep
shoppers in the conversation instead of abandoning it when the network hiccups, so
more chats turn into finished answers and sales.

**Verified in the app.** A real chat turn took about 8 seconds end to end, which is
the window the loading indicator covers. A failed request (the backend returns a
non-2xx, e.g. `422` for an empty message) is what the chat treats as an error, which
triggers the error message and Retry button. The frontend builds and lints clean.

---

## 3. Typo- and synonym-tolerant product search (backend)

**What we added.** The catalogue search now understands similar words and small
typos. Synonyms link related terms — "sweatshirt" finds hoodies and crewnecks,
"sweater" finds fleece, "tee" finds t-shirts, "zip" finds quarter-zips. Typos are
tolerated with fuzzy matching, so "hoodei", "crewnek" and "quater zip" still work.

**Why it helps the shopper.** People don't use the store's exact wording. A shopper
can type the word they know, or fumble the spelling, and still get the right
products instead of an empty "no results."

**Why it helps the business.** Searches that would have returned nothing now return
relevant items, which means fewer dead ends and more products put in front of the
shopper — a direct lift to the chance of a sale.

**Verified in the app.** Through the live chatbot, "do you have any sweatshirts?"
returned crewneck products (the synonym link working). Direct checks against the
database confirm "sweatshirt" surfaces both hoodies and crewnecks, "hoodei",
"crewnek" and "quater zip" return the right items, and a word with no match ("pink",
a color we don't carry) still correctly returns nothing.

---

## 4. The bot asks a follow-up when the request is unclear (backend)

**What we added.** Instead of guessing which product a shopper means, the assistant
asks one short follow-up question when the request is ambiguous — "this"/"it" with no
product page open, a name that matches several different items, or a missing detail
(which college, sport or style). Clear requests (one obvious match, or browsing a
whole type like "hoodies") are still answered directly.

**Why it helps the shopper.** The shopper gets the item they actually meant, not a
confident wrong answer. One quick question is faster than being sent the wrong
product and having to correct it.

**Why it helps the business.** Confirming intent avoids wrong recommendations that
erode trust and create returns. It also keeps answers grounded in the real catalogue,
protecting the shop from the bot inventing or mis-stating a product.

**Verified in the app.** Through the live chatbot, "do you have this?" with no product
page and no prior context replied "Which product do you mean?…" and showed no product
cards — it asked instead of guessing. (When the shopper *is* on a product page, the
page context still lets "this" resolve to that product, so the question is only asked
when it's genuinely needed.)

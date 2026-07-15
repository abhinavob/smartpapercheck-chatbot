# SmartPaperCheck Support Chatbot

An embeddable AI support chatbot that answers questions about a website using RAG
(Retrieval-Augmented Generation) with Voyage AI embeddings and Claude. It grounds every answer in the
site's own content, conversationally schedules product demos, and escalates questions it can't answer to a
human support team. Built for SmartPaperCheck, but configurable to any server-rendered site via one env var.

---

## ✨ What it does

- **Grounded Q&A** — crawls a documentation site into a pgvector knowledge base and answers questions
  strictly from that content (no hallucinated answers).
- **Demo capture** — when a user wants a demo, the bot collects their name, email, phone, and preferred
  time, saves the lead, and emails the admin. (Claude's `register_demo_lead` tool.)
- **Escalation to support** — when the bot can't answer from the knowledge base, or the user asks for a
  human, it collects their name and email, stores their question, and emails the support team so someone
  can follow up. The question is taken from the conversation, so the user is never asked to repeat it.
  (Claude's `escalate_to_human` tool.)

---

## 🛠️ Tech Stack
- **Frontend**: React + Vite (Vanilla CSS)
- **Backend**: FastAPI + Uvicorn (Python, managed with [uv](https://docs.astral.sh/uv/))
- **Database**: Supabase (Postgres + pgvector)
- **LLM**: Claude Sonnet 5 (Anthropic SDK, with tool use)
- **Embeddings**: Voyage AI (`voyage-3`, 1024-dim, cosine, HNSW index)
- **Emails**: Brevo API (transactional SMTP v3)

---

## 🚀 How to Run Locally (Windows)

### Step 1: Configure Environment Variables
Copy `backend/.env.example` to `backend/.env` and fill in your keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
BREVO_API_KEY=your_brevo_api_key
ADMIN_EMAIL=your_email_address_for_alerts
SENDER_EMAIL=your_brevo_verified_sender_email
WEBSITE_URL=https://docs.smart-qna.com
CLAUDE_MODEL=claude-sonnet-5
```
Notes:
- Settings **rejects unknown variables** — do not add keys beyond these, or the app will crash at startup.
- `WEBSITE_URL` must point at a **server-rendered** site. The crawler reads raw HTML and does not execute
  JavaScript, so a client-rendered SPA yields no content. `https://docs.smart-qna.com` (the SmartPaperCheck
  docs) works well.

### Step 2: Database Setup (Supabase)
Go to your **Supabase Dashboard → SQL Editor → New Query**, then paste and run the contents of
[`schema.sql`](./schema.sql). It is idempotent (safe to re-run) and creates everything the app needs:
- `website_pages` — the knowledge base, with an HNSW cosine index
- `demo_leads` — demo requests captured by the bot
- `support_queries` — escalated questions handed off to support
- `match_website_pages` — the similarity-search function used for retrieval

### Step 3: Run the App
The quickest way is the launcher, which starts both services in separate windows. From the **project root**:
```bash
start.bat
```
Or run them manually:
```bash
# Backend — from backend/
uv sync                                        # install deps, Python, and .venv
uv run uvicorn main:app --reload --port 8000   # API + docs at http://localhost:8000/docs

# Frontend — from frontend/, in a second terminal
npm install
npm run dev                                    # UI at http://localhost:5173
```

### Step 4: Ingest the Knowledge Base
Before the bot can answer, it needs content. In the admin dashboard (http://localhost:5173) click
**Scrape**, or call `POST /api/scrape` from http://localhost:8000/docs. This crawls every page of
`WEBSITE_URL`, embeds the text, and stores it. Then open the chat widget and ask away.

---

## 🔌 API Endpoints

| Method | Path                 | Purpose                                                        |
|--------|----------------------|---------------------------------------------------------------|
| POST   | `/api/scrape`        | Crawl `WEBSITE_URL`, chunk, embed, and store the knowledge base |
| POST   | `/api/chat`          | Send a message (+ history); returns the bot's reply            |
| GET    | `/api/leads`         | List captured demo leads                                       |
| GET    | `/api/scraped-urls`  | List URLs currently in the knowledge base                      |
| GET    | `/health`            | Health check                                                   |

---

## ⚙️ How It Works

**Ingestion** (`POST /api/scrape`): `scraper.scrape_site` discovers every same-site link on the base page,
scrapes each page, and combines the text → `chunker` splits it → `embedder` batches it into Voyage
embeddings → `db` stores the chunks under `WEBSITE_URL`.

**Chat** (`POST /api/chat`): the user's message is embedded and matched against the knowledge base
(`match_website_pages`), the top chunks are injected into the system prompt, and Claude either answers from
that context or calls one of two tools — `register_demo_lead` or `escalate_to_human` — which the backend
handles by saving to the database and sending the appropriate Brevo email.

---

## 💻 Code Structure

- **`schema.sql`** — the complete Supabase schema (tables, index, search function).
- **`start.bat`** — launches backend and frontend together.
- **`backend/`**:
  - `main.py` — FastAPI endpoints and the tool-call handling for demo + escalation.
  - `config.py` — env-based settings (`pydantic-settings`; rejects unknown vars).
  - `models.py` — Pydantic request/response schemas.
  - `scraper.py` — crawls a site (`scrape_site`) and extracts page text (`scrape_url`).
  - `chunker.py` — splits text into chunks using LangChain text splitters.
  - `embedder.py` — batches chunks into 1024-dim Voyage embeddings.
  - `db.py` — Supabase client: store/search chunks, save leads and support queries.
  - `agent.py` — the Claude chat loop, system prompt, and the two tools.
  - `email_service.py` — Brevo notifications for demo leads and support queries.
- **`frontend/`**:
  - `src/components/Dashboard.jsx` — admin dashboard: scrape controls and lead table.
  - `src/components/ChatWidget.jsx` — floating chat widget.
  - `src/api/client.js` — API client for the backend endpoints.

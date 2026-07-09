# Website Support & Lead Chatbot

A production-grade, embeddable support chatbot that uses RAG (Retrieval-Augmented Generation) with Voyage AI embeddings and Claude to answer website-specific questions and conversationally schedule product demos.

---

## 🛠️ Tech Stack
- **Frontend**: React + Vite (Vanilla CSS)
- **Backend**: FastAPI + Uvicorn (Python)
- **Database**: Supabase (Postgres + pgvector)
- **LLM**: Claude 3.5 Sonnet
- **Embeddings**: Voyage AI (`voyage-3`)
- **Emails**: Brevo API (SMTP v3)

---

## 🚀 How to Run Locally (Windows)

### Step 1: Configure Environment Variables
Before running, you must open the `backend/.env` file and fill in your keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
BREVO_API_KEY=your_brevo_api_key
ADMIN_EMAIL=your_email_address_for_alerts
SENDER_EMAIL=your_brevo_verified_sender_email
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

---

### Step 2: Database Setup (Supabase)
Go to your **Supabase Dashboard** → **SQL Editor** → **New Query**, and run these SQL statements:

```sql
-- 1. Enable vector extension
create extension if not exists vector;

-- 2. Create website pages table (1024 dims for Voyage-3)
create table if not exists website_pages (
    id            uuid    default gen_random_uuid() primary key,
    url           text    not null,
    chunk_index   integer not null,
    chunk_content text    not null,
    embedding     vector(1024),
    created_at    timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Create HNSW index
create index on website_pages using hnsw (embedding vector_cosine_ops);

-- 4. Create leads table
create table if not exists demo_leads (
    id             uuid default gen_random_uuid() primary key,
    name           text not null,
    email          text not null,
    phone          text not null,
    preferred_time text not null,
    website_url    text not null,
    created_at     timestamp with time zone default timezone('utc', now()) not null
);

-- 5. Create search matching function
create or replace function match_website_pages (
    query_embedding vector(1024),
    match_threshold float,
    match_count     int,
    filter_url      text
)
returns table (
    id            uuid,
    url           text,
    chunk_content text,
    similarity    float
)
language sql stable
as $$
    select
        website_pages.id,
        website_pages.url,
        website_pages.chunk_content,
        1 - (website_pages.embedding <=> query_embedding) as similarity
    from website_pages
    where website_pages.url = filter_url
      and 1 - (website_pages.embedding <=> query_embedding) > match_threshold
    order by website_pages.embedding <=> query_embedding
    limit match_count;
$$;
```

---

### Step 3: Run the Backend
Open a terminal in the `backend/` folder:
```bash
# 1. Activate the virtual environment
.\venv\Scripts\activate

# 2. Run the FastAPI server
uvicorn main:app --reload --port 8000
```
- API Docs will be live at: http://localhost:8000/docs

---

### Step 4: Run the Frontend
Open a new terminal tab in the `frontend/` folder:
```bash
# 1. Start the React development server
npm run dev
```
- Frontend will be live at: http://localhost:5173

---

## 💻 Code Structure

- **`backend/`**:
  - `main.py`: Main FastAPI endpoints (`/api/scrape`, `/api/chat`, `/api/leads`, `/api/scraped-urls`).
  - `scraper.py`: Fetches and extracts body text from any website URL using BeautifulSoup.
  - `chunker.py`: Splits scraped text into semantic pieces using LangChain splitters.
  - `embedder.py`: Embeds chunks to 1024-dimensional vectors using Voyage AI.
  - `db.py`: Connects to Supabase.
  - `agent.py`: Converses with the user via Claude, injecting context and using the lead registration tool.
  - `email_service.py`: Dispatches email notifications using Brevo.

- **`frontend/`**:
  - `src/components/Dashboard.jsx`: Admin dashboard containing the scraper controls and lead tables.
  - `src/components/ChatWidget.jsx`: Floating widget displaying the support conversation bubble.
  - `src/api/client.js`: API client calling backend endpoints.

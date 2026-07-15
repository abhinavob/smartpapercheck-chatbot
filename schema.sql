-- SmartPaperCheck chatbot — Supabase schema.
-- Run this in the Supabase SQL Editor. Safe to re-run (idempotent).

-- 1. Enable vector extension
create extension if not exists vector;

-- 2. Website pages / knowledge base (1024 dims for Voyage-3)
create table if not exists website_pages (
    id            uuid    default gen_random_uuid() primary key,
    url           text    not null,
    chunk_index   integer not null,
    chunk_content text    not null,
    embedding     vector(1024),
    created_at    timestamp with time zone default timezone('utc', now()) not null
);

-- 3. HNSW index for cosine similarity search
create index if not exists website_pages_embedding_idx
    on website_pages using hnsw (embedding vector_cosine_ops);

-- 4. Demo leads — written by Claude's register_demo_lead tool (sales intent)
create table if not exists demo_leads (
    id             uuid default gen_random_uuid() primary key,
    name           text not null,
    email          text not null,
    phone          text not null,
    preferred_time text not null,
    website_url    text not null,
    created_at     timestamp with time zone default timezone('utc', now()) not null
);

-- 5. Support queries — written by Claude's escalate_to_human tool (support intent).
--    Stores a question the bot could not answer, plus the user's contact, for the
--    support team to follow up on.
create table if not exists support_queries (
    id          uuid default gen_random_uuid() primary key,
    name        text not null,
    email       text not null,
    query       text not null,
    website_url text not null,
    created_at  timestamp with time zone default timezone('utc', now()) not null
);

-- 6. Similarity search function
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

from supabase import create_client, Client
from config import settings

supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

def delete_existing_chunks(url: str):
    supabase.table("website_pages").delete().eq("url", url).execute()

def save_chunk(url: str, index: int, chunk: str, embedding: list[float]):
    supabase.table("website_pages").insert({
        "url": url,
        "chunk_index": index,
        "chunk_content": chunk,
        "embedding": embedding
    }).execute()

def get_scraped_urls() -> list[str]:
    result = supabase.table("website_pages").select("url").execute()
    urls = list({row["url"] for row in result.data})
    return urls

def search_similar_chunks(
    query_embedding: list[float],
    url: str,
    top_k: int = 5
) -> list[dict]:
    result = supabase.rpc("match_website_pages", {
        "query_embedding": query_embedding,
        "match_threshold": 0.35,
        "match_count": top_k,
        "filter_url": url
    }).execute()
    return result.data

def save_lead(
    name: str,
    email: str,
    phone: str,
    preferred_time: str,
    website_url: str
):
    supabase.table("demo_leads").insert({
        "name": name,
        "email": email,
        "phone": phone,
        "preferred_time": preferred_time,
        "website_url": website_url
    }).execute()

def get_all_leads() -> list[dict]:
    result = (
        supabase.table("demo_leads")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data

def save_support_query(
    name: str,
    email: str,
    query: str,
    website_url: str
):
    supabase.table("support_queries").insert({
        "name": name,
        "email": email,
        "query": query,
        "website_url": website_url
    }).execute()
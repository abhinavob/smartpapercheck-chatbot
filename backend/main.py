from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models import ScrapeResponse, ChatRequest, ChatResponse
from scraper import scrape_site
from chunker import chunk_text
from embedder import get_embedding, get_embeddings
from db import (delete_existing_chunks, save_chunk, search_similar_chunks, save_lead, get_all_leads, get_scraped_urls)
from agent import chat
from email_service import send_lead_email

app = FastAPI(title="Support Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_endpoint():
    try:
        url = settings.website_url
        if not url:
            raise HTTPException(status_code=400, detail="website_url is not configured in backend .env file.")
            
        raw_text = await scrape_site(url)
        if not raw_text or len(raw_text) < 100:
            raise HTTPException(status_code=400, detail="Could not extract enough text from configured website.")
            
        chunks = chunk_text(raw_text)
        embeddings = await get_embeddings(chunks)

        delete_existing_chunks(url)
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            save_chunk(url=url, index=i, chunk=chunk, embedding=embedding)

        return ScrapeResponse(success=True, chunks_stored=len(chunks), message=f"Successfully scraped and indexed {url}!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(body: ChatRequest):
    try:
        url = settings.website_url
        if not url:
            raise HTTPException(status_code=400, detail="website_url is not configured in backend .env.")
            
        query_embedding = await get_embedding(body.message)
        relevant_chunks = search_similar_chunks(query_embedding, url)
        context_chunks = [c["chunk_content"] for c in relevant_chunks]
        
        history = [{"role": m.role, "content": m.content} for m in body.history]
        result = chat(body.message, history, context_chunks, url)

        if result["type"] == "tool_call" and result["tool_name"] == "register_demo_lead":
            args = result["tool_input"]
            save_lead(args["name"], args["email"], args["phone"], args["preferred_time"], url)
            await send_lead_email(args["name"], args["email"], args["phone"], args["preferred_time"], url)
            return ChatResponse(
                reply=f"✅ Perfect, {args['name']}! Your demo has been scheduled.",
                lead_captured=True
            )

        return ChatResponse(reply=result["text"], lead_captured=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/leads")
def leads_endpoint():
    return get_all_leads()

@app.get("/api/scraped-urls")
def scraped_urls_endpoint():
    return get_scraped_urls()
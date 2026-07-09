from pydantic import BaseModel

class ScrapeRequest(BaseModel):
    url: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    url: str
    history: list[ChatMessage] = []

class ScrapeResponse(BaseModel):
    success: bool
    chunks_stored: int
    message: str

class ChatResponse(BaseModel):
    reply: str
    lead_captured: bool = False
import httpx
from config import settings

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"

HEADERS = {
    "Authorization": f"Bearer {settings.voyage_api_key}",
    "Content-Type": "application/json"
}

async def get_embedding(text: str) -> list[float]:
    clean = text.replace("\n", " ").strip()

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            VOYAGE_URL,
            headers=HEADERS,
            json={
                "input": [clean],
                "model": "voyage-3"
            }
        )
        response.raise_for_status()
        result = response.json()
        
        return result["data"][0]["embedding"]
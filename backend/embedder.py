import httpx
from config import settings

VOYAGE_URL = "https://api.voyageai.com/v1/embeddings"

HEADERS = {
    "Authorization": f"Bearer {settings.voyage_api_key}",
    "Content-Type": "application/json"
}

BATCH_SIZE = 100


async def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Embed many texts with as few Voyage requests as possible.

    One request per BATCH_SIZE inputs instead of one per text — this is what
    keeps a full-site ingest under Voyage's rate limit. Returns embeddings in
    the same order as texts.
    """
    cleaned = [t.replace("\n", " ").strip() for t in texts]
    embeddings: list[list[float]] = []

    async with httpx.AsyncClient(timeout=60.0) as client:
        for start in range(0, len(cleaned), BATCH_SIZE):
            batch = cleaned[start:start + BATCH_SIZE]
            response = await client.post(
                VOYAGE_URL,
                headers=HEADERS,
                json={"input": batch, "model": "voyage-3"}
            )
            response.raise_for_status()
            data = sorted(response.json()["data"], key=lambda item: item["index"])
            embeddings.extend(item["embedding"] for item in data)

    return embeddings


async def get_embedding(text: str) -> list[float]:
    embeddings = await get_embeddings([text])
    return embeddings[0]
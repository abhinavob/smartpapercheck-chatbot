import httpx
from bs4 import BeautifulSoup

USEFUL_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "td", "th", "blockquote", "article",
    "section", "span", "div"
]

JUNK_TAGS = [
    "script", "style", "nav", "footer", "header",
    "noscript", "form", "svg", "img", "button",
    "iframe", "aside", "meta", "link"
]

async def scrape_url(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(JUNK_TAGS):
        tag.decompose()

    text_parts = []
    for tag in soup.find_all(USEFUL_TAGS):
        text = tag.get_text(separator=" ", strip=True)
        if len(text) > 40:
            text_parts.append(text)

    seen = set()
    unique_parts = []
    for part in text_parts:
        if part not in seen:
            seen.add(part)
            unique_parts.append(part)

    return "\n\n".join(unique_parts)
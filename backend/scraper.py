from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

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
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url, headers=HEADERS)
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


async def discover_pages(base_url: str) -> list[str]:
    """Return the base page plus every same-site link found in its raw HTML.

    Link discovery reads the unstripped HTML because scrape_url() removes the
    <nav> that holds a docs sidebar. Fragments and external hosts are dropped.
    """
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(base_url, headers=HEADERS)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    base_host = urlparse(base_url).netloc

    pages = {base_url.rstrip("/")}
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].split("#")[0].strip()
        if not href:
            continue
        absolute = urljoin(base_url, href)
        parsed = urlparse(absolute)
        if parsed.scheme in ("http", "https") and parsed.netloc == base_host:
            pages.add(absolute.rstrip("/"))

    return sorted(pages)


async def scrape_site(base_url: str) -> str:
    """Crawl every internal page linked from base_url and return combined text.

    Each page is scraped with scrape_url() and tagged with its source URL. Pages
    that fail or yield too little text are skipped so one bad page can't sink the
    whole ingest.
    """
    pages = await discover_pages(base_url)

    sections = []
    for page in pages:
        try:
            text = await scrape_url(page)
        except httpx.HTTPError:
            continue
        if text and len(text) > 100:
            sections.append(f"Source: {page}\n\n{text}")

    return "\n\n\n".join(sections)
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function scrapeWebsite() {
    const res = await fetch(`${BASE}/api/scrape`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Scraping failed");
    }
    return res.json();
}

export async function sendMessage(message, history) {
    const res = await fetch(`${BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, history })
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Chat error");
    }
    return res.json();
}

export async function getLeads() {
    const res = await fetch(`${BASE}/api/leads`);
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to fetch leads");
    }
    return res.json();
}

export async function getScrapedUrls() {
    const res = await fetch(`${BASE}/api/scraped-urls`);
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to fetch scraped URLs");
    }
    return res.json();
}

import React, { useState } from "react";
import { scrapeWebsite } from "../api/client";

export default function ScrapeForm({ onSuccess }) {
    const [status, setStatus] = useState(null); // null | "loading" | "success" | "error"
    const [message, setMessage] = useState("");

    const handleScrape = async () => {
        setStatus("loading");
        setMessage("");

        try {
            const data = await scrapeWebsite();
            setStatus("success");
            setMessage(`✅ Successfully crawled! ${data.message}`);
            if (onSuccess) onSuccess();
        } catch (err) {
            setStatus("error");
            setMessage(`❌ Error: ${err.message}`);
        }
    };

    return (
        <div className="card">
            <div className="card-title">⚙️ Knowledge Ingestion</div>
            <p className="text-sm" style={{ color: "var(--text-secondary)", marginBottom: 16 }}>
                Click below to scrape and update the knowledge base of the website configured in your backend settings.
            </p>
            <button
                id="scrape-submit-button"
                className="btn btn-primary"
                onClick={handleScrape}
                disabled={status === "loading"}
                style={{ width: "100%", justifyContent: "center" }}
            >
                {status === "loading" ? (
                    <>
                        <span className="spinner" /> Crawling Site Content...
                    </>
                ) : (
                    "Scrape Website"
                )}
            </button>
            {message && (
                <p className={`mt-4 text-sm ${status === "success" ? "text-success" : "text-error"}`}>
                    {message}
                </p>
            )}
        </div>
    );
}

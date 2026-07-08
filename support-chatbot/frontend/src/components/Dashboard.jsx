import React, { useState, useEffect } from "react";
import ScrapeForm from "./ScrapeForm";
import LeadTable from "./LeadTable";
import { useLeads } from "../hooks/useLeads";
import { getScrapedUrls } from "../api/client";

export default function Dashboard({ onTestChat }) {
    const { leads, loading, refresh } = useLeads();
    const [scrapedUrls, setScrapedUrls] = useState([]);
    const [urlsLoading, setUrlsLoading] = useState(true);

    const fetchUrls = async () => {
        setUrlsLoading(true);
        try {
            const data = await getScrapedUrls();
            setScrapedUrls(data);
        } catch (err) {
            console.error("Failed to load active sites", err);
        } finally {
            setUrlsLoading(false);
        }
    };

    useEffect(() => {
        fetchUrls();
    }, []);

    const handleScrapeSuccess = () => {
        fetchUrls();
        refresh(); // Refresh leads table
    };

    return (
        <div className="main-content">
            <div className="page-header">
                <h1 className="page-title">Admin Dashboard</h1>
                <p className="page-subtitle">Configure the knowledge base of the support chatbot and view captured leads.</p>
            </div>

            <div className="grid-2">
                <ScrapeForm onSuccess={handleScrapeSuccess} />
                
                <div className="card">
                    <div className="card-title">📖 Active Scraped Site</div>
                    {urlsLoading ? (
                        <div className="spinner" />
                    ) : scrapedUrls.length === 0 ? (
                        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                            No website has been indexed yet. Click "Scrape Website" to crawl the site configured in your settings.
                        </p>
                    ) : (
                        <div>
                            <p className="text-sm" style={{ color: "var(--text-secondary)", marginBottom: 12 }}>
                                The chatbot is currently loaded with knowledge from:
                            </p>
                            <div 
                                style={{ 
                                    background: "rgba(99, 102, 241, 0.1)", 
                                    padding: "10px 14px", 
                                    borderRadius: "var(--radius-sm)", 
                                    border: "1px solid rgba(99, 102, 241, 0.2)",
                                    wordBreak: "break-all",
                                    fontWeight: 500,
                                    color: "var(--accent-light)",
                                    marginBottom: 16
                                }}
                            >
                                {scrapedUrls[0]}
                            </div>
                            <button 
                                id="test-chatbot-button"
                                className="btn btn-primary" 
                                style={{ width: "100%", justifyContent: "center" }}
                                onClick={onTestChat}
                            >
                                💬 Open Chat Widget
                            </button>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-6">
                <LeadTable leads={leads} loading={loading} onRefresh={refresh} />
            </div>
        </div>
    );
}

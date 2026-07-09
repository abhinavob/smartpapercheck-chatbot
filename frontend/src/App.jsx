import React, { useState } from "react";
import Dashboard from "./components/Dashboard";
import ChatWidget from "./components/ChatWidget";
import "./App.css";

export default function App() {
    const [activeTab, setActiveTab] = useState("dashboard");

    return (
        <div className="app">
            {/* Navbar */}
            <nav className="navbar">
                <div className="navbar-logo">
                    <div className="navbar-logo-icon">🤖</div>
                    SupportBot
                </div>

                <div className="nav-tabs">
                    <button
                        id="nav-dashboard-tab"
                        className={`nav-tab ${activeTab === "dashboard" ? "active" : ""}`}
                        onClick={() => setActiveTab("dashboard")}
                    >
                        🏠 Dashboard
                    </button>
                    <button
                        id="nav-chat-tab"
                        className={`nav-tab ${activeTab === "chat" ? "active" : ""}`}
                        onClick={() => setActiveTab("chat")}
                    >
                        💬 Test Chat
                    </button>
                </div>

                <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
                    Claude + Voyage AI
                </div>
            </nav>

            {/* Main content area */}
            {activeTab === "dashboard" && (
                <Dashboard onTestChat={() => setActiveTab("chat")} />
            )}

            {activeTab === "chat" && (
                <div className="main-content">
                    <div className="page-header">
                        <h1 className="page-title">💬 Test Your Chatbot</h1>
                        <p className="page-subtitle">
                            Interacting with the pre-configured customer support agent.
                        </p>
                    </div>
                    <div className="card" style={{ minHeight: 300, display: "flex", alignItems: "center", justifyContent: "center", borderStyle: "dashed" }}>
                        <div style={{ textAlign: "center", color: "var(--text-muted)" }}>
                            <p style={{ fontSize: 18, marginBottom: 8 }}>Conversational Widget Loaded</p>
                            <p className="text-sm">Click the floating 💬 bubble at the bottom-right of the screen to start chatting.</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Floating chat widget — always enabled */}
            <ChatWidget />
        </div>
    );
}

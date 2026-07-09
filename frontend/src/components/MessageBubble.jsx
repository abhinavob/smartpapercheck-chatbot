import React from "react";

export default function MessageBubble({ role, content }) {
    const isUser = role === "user";
    return (
        <div className={`message-row ${isUser ? "user" : ""}`}>
            {!isUser && <div className="message-avatar">🤖</div>}
            <div className={`message-bubble ${isUser ? "user" : "bot"}`}>
                {content}
            </div>
            {isUser && <div className="message-avatar user-avatar">👤</div>}
        </div>
    );
}

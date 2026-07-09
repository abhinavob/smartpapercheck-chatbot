import React, { useState, useRef, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

export default function ChatWidget() {
    const [open, setOpen] = useState(false);
    const [input, setInput] = useState("");
    const { messages, isLoading, send } = useChat();
    const bottomRef = useRef(null);

    useEffect(() => {
        if (open) {
            bottomRef.current?.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages, isLoading, open]);

    const handleSend = () => {
        if (!input.trim()) return;
        send(input);
        setInput("");
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            <button 
                id="chat-toggle-button"
                className="chat-toggle-btn" 
                onClick={() => setOpen(o => !o)}
                title="Open Support Chat"
            >
                {open ? "✕" : "💬"}
            </button>
            {open && (
                <div className="chat-window" id="chat-container">
                    <div className="chat-header">
                        <div className="chat-header-avatar">🤖</div>
                        <div className="chat-header-info">
                            <div className="chat-header-name">Support Agent</div>
                            <div className="chat-header-status">
                                <span className="online-dot" /> Online · Powered by Claude
                            </div>
                        </div>
                        <button className="chat-close-btn" onClick={() => setOpen(false)}>✕</button>
                    </div>
                    <div className="messages-area">
                        {messages.map(m => (
                            <MessageBubble key={m.id} role={m.role} content={m.content} />
                        ))}
                        {isLoading && <TypingIndicator />}
                        <div ref={bottomRef} />
                    </div>
                    <div className="chat-input-area">
                        <textarea
                            id="chat-text-input"
                            className="chat-input"
                            rows={1}
                            placeholder="Type a message..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                        />
                        <button
                            id="chat-submit-button"
                            className="chat-send-btn"
                            onClick={handleSend}
                            disabled={isLoading || !input.trim()}
                        >
                            ➤
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}

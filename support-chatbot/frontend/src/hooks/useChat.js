import { useState } from "react";
import { sendMessage } from "../api/client";

export function useChat() {
    const [messages, setMessages] = useState([
        {
            id: 0,
            role: "assistant",
            content: "👋 Hi! I'm your support assistant. Ask me anything about our website, or say 'I'd like a demo' to schedule one!"
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [leadCaptured, setLeadCaptured] = useState(false);

    const send = async (text) => {
        if (!text.trim() || isLoading) return;

        const userMsg = { id: Date.now(), role: "user", content: text };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);

        try {
            // Format history in the schema Claude expects
            const history = messages
                .filter(m => m.id !== 0) // exclude welcome message
                .map(m => ({ role: m.role, content: m.content }));

            const data = await sendMessage(text, history);
            const botMsg = { id: Date.now() + 1, role: "assistant", content: data.reply };
            setMessages(prev => [...prev, botMsg]);
            if (data.lead_captured) setLeadCaptured(true);
        } catch (err) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                role: "assistant",
                content: "⚠️ I'm having trouble connecting right now. Please try again."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return { messages, isLoading, leadCaptured, send };
}

import anthropic
from config import settings

claude = anthropic.Anthropic(api_key=settings.anthropic_api_key)

TOOLS = [
    {
        "name": "register_demo_lead",
        "description": (
            "Use this tool to register a demo request from a user. "
            "IMPORTANT RULES: "
            "1. Only call this after you have collected ALL 4 required details from the user. "
            "2. Ask for each detail one at a time, naturally in the conversation. "
            "3. Required details: full name, email address, phone number, preferred demo time. "
            "4. Confirm each detail with the user before calling. "
            "5. NEVER call this tool with missing or placeholder values."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name"},
                "email": {"type": "string", "description": "Valid email address"},
                "phone": {"type": "string", "description": "Phone number"},
                "preferred_time": {"type": "string", "description": "Preferred date and time for demo"}
            },
            "required": ["name", "email", "phone", "preferred_time"]
        }
    }
]

def build_system_prompt(context_chunks: list[str], website_url: str) -> str:
    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "No specific content found."
    return f"""You are a friendly support agent for the website: {website_url}

YOUR RULES:
1. Answer ONLY based on the KNOWLEDGE BASE below.
2. Keep answers concise.
3. If the user asks for a demo, ask for their details ONE AT A TIME: Name → Email → Phone → Preferred Time.
4. Once you have ALL 4, call the register_demo_lead tool immediately.
5. Never make up information.

=== KNOWLEDGE BASE ===
{context}
=== END KNOWLEDGE BASE ==="""

def chat(
    user_message: str,
    history: list[dict],
    context_chunks: list[str],
    website_url: str
) -> dict:
    system_prompt = build_system_prompt(context_chunks, website_url)
    messages = list(history) + [{"role": "user", "content": user_message}]

    response = claude.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=system_prompt,
        tools=TOOLS,
        messages=messages
    )

    for block in response.content:
        if block.type == "tool_use":
            return {
                "type": "tool_call",
                "tool_name": block.name,
                "tool_input": block.input
            }

    text = next((block.text for block in response.content if hasattr(block, "text")), "Error")
    return {"type": "text", "text": text}
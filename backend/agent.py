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
    },
    {
        "name": "escalate_to_human",
        "description": (
            "Use this tool to hand a user off to the human support team when you "
            "CANNOT answer their question from the knowledge base, or when the user "
            "explicitly asks to talk to a person. "
            "IMPORTANT RULES: "
            "1. Only call this after you have collected the user's full name and email. "
            "2. Ask for name and email one at a time, naturally in the conversation. "
            "3. Do NOT ask the user to restate their question — they already asked it. Fill the query "
            "field yourself from what they said earlier in the conversation. "
            "4. Confirm the details with the user before calling. "
            "5. NEVER call this tool with missing or placeholder values."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name"},
                "email": {"type": "string", "description": "Valid email address"},
                "query": {"type": "string", "description": "The user's question or issue, taken from what they already asked earlier in the conversation"}
            },
            "required": ["name", "email", "query"]
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
6. If you CANNOT answer from the knowledge base, or the user asks to speak to a human, offer to
   connect them to the support team. They already told you their question, so do NOT ask for it again —
   just collect Name → Email, ONE AT A TIME. Then call escalate_to_human, filling the query field with
   the question they already asked.

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
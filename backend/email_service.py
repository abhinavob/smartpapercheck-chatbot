import httpx
from config import settings

async def send_lead_email(
    name: str,
    email: str,
    phone: str,
    preferred_time: str,
    website_url: str
) -> int:
    html = f"""
    <h2>New Demo Request!</h2>
    <p><b>Name:</b> {name}</p>
    <p><b>Email:</b> {email}</p>
    <p><b>Phone:</b> {phone}</p>
    <p><b>Time:</b> {preferred_time}</p>
    <p><b>Website:</b> {website_url}</p>
    """

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": settings.brevo_api_key,
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            json={
                "sender": {
                    "name": "Support Bot",
                    "email": settings.sender_email
                },
                "to": [
                    {
                        "email": settings.admin_email,
                        "name": "Admin"
                    }
                ],
                "subject": f"New Demo Lead: {name}",
                "htmlContent": html
            }
        )
        return response.status_code
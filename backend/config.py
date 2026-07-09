from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_service_role_key: str
    anthropic_api_key: str
    voyage_api_key: str
    brevo_api_key: str                        # API Key for Brevo SMTP service
    admin_email: str                          # Recipient email for alerts
    sender_email: str                         # Brevo-verified sender email address
    website_url: str                          # The specific website URL to scrape and chat about
    claude_model: str = "claude-sonnet-5"

    class Config:
        env_file = ".env"

# Create one single instance
settings = Settings()
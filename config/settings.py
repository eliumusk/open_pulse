"""
Configuration settings for Open Pulse
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Database settings
DATABASE_FILE = os.getenv("DATABASE_URL", "sqlite:///./open_pulse.db")
if DATABASE_FILE.startswith("sqlite:///"):
    DATABASE_FILE = DATABASE_FILE.replace("sqlite:///", "")
    DATABASE_FILE = str(PROJECT_ROOT / DATABASE_FILE)
else:
    DATABASE_FILE = DATABASE_FILE

# LLM API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# AgentOS Configuration
AGENTOS_PORT = int(os.getenv("AGENTOS_PORT", "7777"))
AGENTOS_HOST = os.getenv("AGENTOS_HOST", "0.0.0.0")

# Scheduler Configuration
NEWSLETTER_GENERATION_HOUR = int(os.getenv("NEWSLETTER_GENERATION_HOUR", "8"))
NEWSLETTER_GENERATION_MINUTE = int(os.getenv("NEWSLETTER_GENERATION_MINUTE", "0"))

# Telemetry
AGNO_TELEMETRY = os.getenv("AGNO_TELEMETRY", "false").lower() == "true"

# Validate required settings
def validate_settings():
    """Validate that required settings are present"""
    if not OPENAI_API_KEY and not ANTHROPIC_API_KEY and not OPENROUTER_API_KEY:
        raise ValueError(
            "At least one LLM API key must be set: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, or OPENROUTER_API_KEY"
        )
    return True


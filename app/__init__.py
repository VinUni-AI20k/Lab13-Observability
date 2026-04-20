from __future__ import annotations

from dotenv import load_dotenv

# Load environment variables as early as possible so Langfuse and the rest of
# the app can read configuration from a local `.env` file during development.
load_dotenv()

__all__ = []

"""App settings, read from environment variables or backend/.env (see .env.example)."""
import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BACKEND_DIR.parent / "database"


def _load_env_file(path: Path):
    # Minimal .env reader: KEY=value lines, # comments. Real env vars take priority.
    if not path.exists():
        return
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    for key, value in values.items():
        os.environ.setdefault(key, value)


_load_env_file(BACKEND_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{DB_DIR / 'shop.db'}"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
SESSION_TTL_HOURS = float(os.getenv("SESSION_TTL_HOURS", "12"))
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@example.com")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "demo1234")

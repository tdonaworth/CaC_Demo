"""Runtime configuration, read from environment variables.

In ECS these come from the task definition: plain values via `environment`,
secrets (API_KEYS, DATABASE_URL) via `secrets` -> AWS Secrets Manager.
"""
import os


def load() -> dict:
    return {
        "DATABASE_URL": os.environ.get("DATABASE_URL", "sqlite:///local.db"),
        # Comma-separated list of accepted API keys. Empty => all authenticated
        # routes reject (fail closed).
        "API_KEYS": [k for k in os.environ.get("API_KEYS", "").split(",") if k],
        "ENVIRONMENT": os.environ.get("APP_ENVIRONMENT", "development"),
        "MAX_NOTE_LENGTH": int(os.environ.get("MAX_NOTE_LENGTH", "2000")),
    }

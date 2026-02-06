# src/database/models.py
"""
DEPRECATED â€” This file is NOT used in production.

The canonical database schema lives in:
    src/api/schema.py  (SQLAlchemy models matching the real aria_warehouse DB)

The production database connects via:
    aria_skills/api_client  â†’ HTTP to aria-api (preferred)
    aria_skills/database    â†’ Direct asyncpg to PostgreSQL (last resort)

This file remains only for reference. Do NOT import from here.
"""
raise ImportError(
    "src/database/models.py is deprecated. "
    "Use src/api/schema.py for DB models or aria_skills/api_client for data access."
)

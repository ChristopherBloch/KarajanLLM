#!/usr/bin/env python3
"""
Ingest Aria Mind files (Markdown/YAML) into the PostgreSQL database.
Running this script will populate:
- goals (from aria_mind/GOALS.md)
- memories (from aria_mind/MEMORY.md)
- scheduled_jobs (from aria_mind/cron_jobs.yaml)

Usage:
    python3 scripts/ingest_mind.py
"""
import os
import re
import yaml
import asyncio
import asyncpg
from datetime import datetime

# Configuration
DB_USER = os.getenv("DB_USER", "aria_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "d2dc6208ae184542abecdfd1")
DB_NAME = os.getenv("DB_NAME", "aria_warehouse")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Paths (relative to script location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MIND_DIR = os.path.join(SCRIPT_DIR, "../aria_mind")

GOALS_FILE = os.path.join(MIND_DIR, "GOALS.md")
MEMORY_FILE = os.path.join(MIND_DIR, "MEMORY.md")
CRON_FILE = os.path.join(MIND_DIR, "cron_jobs.yaml")

async def get_db_connection():
    # If running outside docker, might need to map port or use docker exec.
    # Assuming running from host where port 5432 is exposed.
    dsn = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    try:
        return await asyncpg.connect(dsn)
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

async def ingest_cron_jobs(conn):
    if not os.path.exists(CRON_FILE):
        print(f"Warning: {CRON_FILE} not found.")
        return

    print(f"Processing {CRON_FILE}...")
    with open(CRON_FILE, 'r') as f:
        data = yaml.safe_load(f)

    jobs = data.get('jobs', [])
    count = 0
    for job in jobs:
        # Upsert job
        await conn.execute("""
            INSERT INTO scheduled_jobs (name, cron_schedule, agent, message, parameters, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5::jsonb, NOW(), NOW())
            ON CONFLICT (name) DO UPDATE 
            SET cron_schedule = $2, agent = $3, message = $4, parameters = $5::jsonb, updated_at = NOW()
        """, 
        job.get('name'),
        job.get('cron') or job.get('every'), # simple mapping, might need adjustment if schema is strict
        job.get('agent', 'main'),
        job.get('message', ''),
        '{}' # parameters defaults to empty json
        )
        count += 1
    print(f"  -> Ingested {count} jobs.")

async def ingest_memories(conn):
    if not os.path.exists(MEMORY_FILE):
        print(f"Warning: {MEMORY_FILE} not found.")
        return

    print(f"Processing {MEMORY_FILE}...")
    with open(MEMORY_FILE, 'r') as f:
        content = f.read()

    # Simple parsing logic: assume H3 headers are categories, bullets are memories
    # This is a heuristic.
    current_category = "general"
    count = 0
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('### '):
            current_category = line.replace('###', '').strip().lower().replace(' ', '_')
        elif line.startswith('- '):
            memory_text = line[2:].strip()
            if not memory_text: continue
            
            # Key generation (simple hash or slug)
            key = f"mem_{current_category}_{hash(memory_text) % 100000}"
            
            # Upsert
            # Assuming memories table has columns: key, value (jsonb), category
            await conn.execute("""
                INSERT INTO memories (id, key, value, category, created_at, updated_at)
                VALUES (uuid_generate_v4(), $1, $2::jsonb, $3, NOW(), NOW())
                ON CONFLICT (key) DO NOTHING
            """, key, f'"{memory_text}"', current_category)
            count += 1
            
    print(f"  -> Ingested {count} memories.")

async def ingest_goals(conn):
    # This is trickier as GOALS.md is mostly documentation, not a list of active goals.
    # However, we can create some initial seed goals if the table is empty.
    
    count = await conn.fetchval("SELECT count(*) FROM goals")
    if count > 0:
        print("Goals table not empty, skipping seed ingestion.")
        return

    print("Seeding initial goals...")
    initial_goals = [
        ("Restore Aria Memory", "Ingest knowledge from markdown files", 1, "completed"),
        ("Establish Backup Routine", "Create daily backup cron job", 1, "active"),
        ("Verify System Health", "Check all services and logs", 2, "active"),
        ("Learn About Self", "Read MEMORY.md and SOUL.md", 3, "pending")
    ]
    
    for title, desc, prio, status in initial_goals:
         await conn.execute("""
            INSERT INTO goals (title, description, priority, status, created_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, title, desc, prio, status)
    
    print(f"  -> Seeded {len(initial_goals)} goals.")

async def main():
    conn = await get_db_connection()
    if not conn:
        return

    try:
        await ingest_cron_jobs(conn)
        await ingest_memories(conn)
        await ingest_goals(conn)
        print("Done.")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())

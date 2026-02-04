# Lessons

## General
- Do not use SSH or remote commands unless explicitly requested; prefer local scripts that the user can run on the server.
- Avoid writing secrets or tokens into repo files; prompt for them at runtime or keep them unset by default.
- When refactoring skills, verify file content after edits to avoid duplicated blocks and syntax errors; re-read the file before running tests.

## OpenClaw Integration (2026-02-04)

### Architecture Discrepancy
- **OpenClaw uses markdown files for Soul**, not the Python `aria_mind/soul/` code:
  - `SOUL.md` - Core identity (currently empty, says "read soul repo")
  - `IDENTITY.md` - Name, creature, vibe, emoji (template not filled)
  - `BOOTSTRAP.md` - Awakening protocol and system prompt
- The Python soul code (`aria_mind/soul/focus.py`, `values.py`, etc.) is **NOT used by clawdbot** 
- To fix: Either populate the markdown files OR create a bridge that reads from Python soul

### Skill Execution Errors from Logs
1. **File path errors**: Aria looks for `aria_skills/database.py` but skills are in subdirs (`aria_skills/database/__init__.py`)
2. **JSON parsing errors**: `run_skill.py` gets malformed JSON args - need better arg handling
3. **Missing commands**: `aria-apiclient` command not found - OpenClaw tries `exec aria-apiclient` but it's a Python class

### Skill Issues Found by Aria's Self-Audit
- **HIGH: In-memory data loss** - knowledge_graph, social, moltbook lose data on restart
- **HIGH: Pytest runner path injection** - accepts unvalidated path parameter  
- **HIGH: DB query validation** - no validation on raw SQL queries
- **MEDIUM: No rate limiting** - skills can be called unlimited times
- **MEDIUM: API keys could leak to logs** - no redaction in httpx logging

### Database Schema Discovery
- Tables: `goals`, `thoughts`, `memories`, `activity_log`, `knowledge_entities`, `knowledge_relations`, `hourly_goals`, `heartbeat_log`, `performance_log`, `security_events`, `social_posts`, `scheduled_jobs`, `schedule_tick`, `pending_complex_tasks`
- Connection: `postgresql://aria_admin:***@aria-db:5432/aria_warehouse`
- Aria already persists goals and thoughts to DB ✅

### OpenRouter Free Models Issue
- Free tier models returning empty responses - may need fallback handling
- Aria noted: "Both free model tests came back empty"

### What Aria Did Right
- Created 16 goals with proper persistence
- Completed security audit and documented findings
- Researched income strategies (crypto staking, bug bounties)
- Used parameterized SQL queries (no injection in actual usage)

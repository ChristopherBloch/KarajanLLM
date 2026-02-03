# ARIA MANUAL - Deployment & Operations Guide

Complete deployment and operations guide for the Aria stack with OpenClaw integration.

---

## Architecture Overview

Aria runs on [OpenClaw](https://openclaw.ai) with a **local-first** LLM strategy:

```
┌──────────────────────────────────────────────────────────────────┐
│  OpenClaw Gateway (clawdbot)                                      │
│  ├── Model: litellm/qwen3-mlx (primary - MLX on Apple Silicon)   │
│  ├── Fallbacks: glm-free, deepseek-free, kimi (paid last resort) │
│  └── Workspace: aria_mind/ (mounted read-only)                   │
├──────────────────────────────────────────────────────────────────┤
│  LiteLLM Router → MLX Server (port 8080, Metal GPU)              │
│  Model: nightmedia/Qwen3-VLTO-8B-Instruct-qx86x-hi-mlx           │
├──────────────────────────────────────────────────────────────────┤
│  PostgreSQL: aria_warehouse (Aria) + litellm (LiteLLM separate)  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- **macOS with Apple Silicon** (M1/M2/M3/M4) for Metal GPU acceleration
- Docker & Docker Compose
- Git
- SSH access to Mac Mini (for remote deployment)

---

## Quick Deploy (One-Button)

### 1. Clone Repository

```bash
git clone https://github.com/Najia-afk/Aria_moltbot.git
cd Aria_moltbot/stacks/brain
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your values
```

### 3. Start MLX Server (Metal GPU - REQUIRED)

On macOS with Apple Silicon, MLX runs natively for GPU acceleration:

```bash
# Install MLX LM
pip install mlx-lm

# Start MLX server as launchd service (recommended)
# Or manually:
mlx_lm.server --model nightmedia/Qwen3-VLTO-8B-Instruct-qx86x-hi-mlx --host 0.0.0.0 --port 8080 &
```

**Performance:**
- MLX Server (Metal GPU): ~25-35 tokens/second
- Fully utilizes Apple Silicon Neural Engine

### 4. Start Docker Stack

```bash
docker compose up -d
docker compose ps  # Should show 12 healthy containers
```

### 5. Verify OpenClaw

```bash
# Check OpenClaw gateway health
curl http://localhost:18789/health

# Check agent identity
docker exec clawdbot openclaw agents list
# Expected: "main (default), Identity: ⚡️ Aria Blue, Model: litellm/qwen3-local"

# Check status
docker exec clawdbot openclaw status
```

---

## API Keys Required

Configure these in `stacks/brain/.env`:

### Moonshot/Kimi (Paid fallback - last resort)
1. Go to https://platform.moonshot.cn/
2. Register and get API key
3. Add to `.env`: `MOONSHOT_KIMI_KEY=your_key_here`

### OpenRouter (FREE models - recommended fallback)
1. Go to https://openrouter.ai/
2. Get free API key
3. Add to `.env`: `OPEN_ROUTER_KEY=sk-or-v1-...`

FREE models available via OpenRouter:
- `glm-free` - GLM 4.5 Air (131K context)
- `deepseek-free` - DeepSeek R1 0528 (164K context, reasoning)
- `nemotron-free` - Nemotron 30B (256K context)
- `gpt-oss-free` - GPT-OSS 120B (131K context, reasoning)

---

## Database Architecture

**CRITICAL**: Aria and LiteLLM use **separate PostgreSQL databases** to prevent schema conflicts.

| Database | Purpose | Tables |
|----------|---------|--------|
| `aria_warehouse` | Aria's data | activity_log, memories, thoughts, goals, social_posts, heartbeat_log, knowledge_entities, knowledge_relations |
| `litellm` | LiteLLM internal | LiteLLM_* tables (Prisma-managed) |

This separation prevents LiteLLM's Prisma migrations from dropping Aria's tables.

### Database Initialization

The `init-scripts/` folder runs on first PostgreSQL startup:

1. `00-create-litellm-db.sh` - Creates the separate `litellm` database
2. `01-schema.sql` - Creates Aria's 8 core tables with seed data

### Manual Database Access

```bash
# Connect to aria_warehouse
docker exec -it aria-db psql -U aria_admin -d aria_warehouse

# Connect to litellm
docker exec -it aria-db psql -U aria_admin -d litellm

# List all tables
\dt
```

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| traefik | 80/443 | HTTPS routing & reverse proxy |
| aria-db | 5432 | PostgreSQL 16 (internal) |
| aria-api | 8000 | FastAPI backend |
| aria-web | 5000 | Flask UI portal |
| litellm | 18793 | LLM router (external) / 4000 (internal) |
| clawdbot | 18789 | OpenClaw gateway |
| grafana | 3001 | Monitoring dashboards |
| prometheus | 9090 | Metrics collection |
| pgadmin | 5050 | Database admin UI |

---

## OpenClaw Configuration

### Model Configuration

OpenClaw is configured via `openclaw-entrypoint.sh` which generates `/root/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "model": {
        "primary": "litellm/qwen3-local",
        "fallbacks": ["litellm/kimi-local"]
      }
    }
  },
  "models": {
    "providers": {
      "litellm": {
        "baseUrl": "http://litellm:4000/v1/",
        "apiKey": "${CLAWDBOT_TOKEN}"
      }
    }
  }
}
```

### Workspace Mount

The `aria_mind/` folder is mounted to OpenClaw at `/root/.openclaw/workspace/`:

```yaml
# docker-compose.yml volumes for clawdbot
volumes:
  - ../../aria_mind:/root/.openclaw/workspace              # Workspace (read-write for memory)
  - ../../aria_skills:/root/.openclaw/workspace/skills/aria_skills:ro  # Python skills + manifests
  - ../../aria_agents:/root/.openclaw/workspace/skills/aria_agents:ro  # Agent orchestration
  - ../../skills:/root/.openclaw/workspace/skills/legacy:ro            # Legacy skills (deprecated)
```

> **Note**: The entrypoint script creates symlinks from `/root/.openclaw/skills/aria-<skill>/` to each `skill.json` in `aria_skills/<skill>/` at container startup.

Files available to OpenClaw:
- `SOUL.md` - Persona and boundaries
- `IDENTITY.md` - Name: Aria Blue ⚡️
- `AGENTS.md` - Sub-agent definitions
- `TOOLS.md` - Available skills & execution guide
- `HEARTBEAT.md` - Scheduled task checklist
- `MEMORY.md` - Long-term memory (read-write)
- `USER.md` - User profile
- `skills/` - Python skill modules

---

## Python Skills Integration

### Skill Execution

Aria's Python skills are mounted in the OpenClaw workspace and executed via the `exec` tool:

```bash
# Run a skill function
python3 /root/.openclaw/workspace/skills/run_skill.py <skill> <function> '<args_json>'

# Examples:
python3 run_skill.py database query '{"sql": "SELECT COUNT(*) FROM activity_log"}'
python3 run_skill.py moltbook post_status '{"content": "Hello world!"}'
python3 run_skill.py health check_health '{}'
python3 run_skill.py goals list_goals '{"status": "active"}'
```

### Available Skills

| Skill | Module | Functions |
|-------|--------|-----------|
| `database` | `aria_skills.database` | `query`, `execute`, `store_thought`, `store_memory` |
| `moltbook` | `aria_skills.moltbook` | `post_status`, `get_timeline`, `reply_to`, `get_notifications` |
| `health` | `aria_skills.health` | `check_health`, `get_metrics`, `report_error` |
| `goals` | `aria_skills.goals` | `create_goal`, `update_progress`, `list_goals`, `schedule_task` |
| `knowledge_graph` | `aria_skills.knowledge_graph` | `add_entity`, `add_relation`, `query_related`, `search` |
| `llm` | `aria_skills.llm` | `generate`, `chat` |

### Environment Variables for Skills

```env
DATABASE_URL=postgresql://aria_admin:password@aria-db:5432/aria_warehouse
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=hf.co/unsloth/GLM-4.7-Flash-REAP-23B-A3B-GGUF:Q3_K_S
MOLTBOOK_TOKEN=moltbook_sk_...your_token_here
MOLTBOOK_API_URL=https://www.moltbook.com/api/v1
PYTHONPATH=/root/.openclaw/workspace:/root/.openclaw/workspace/skills
```

---

## OpenClaw Skills (UI)

Skills visible in the OpenClaw UI (`/clawdbot/skills`) are now consolidated in `aria_skills/<skill>/`:

| Skill | Emoji | Description |
|-------|-------|-------------|
| aria-database | 🗄️ | Query PostgreSQL database |
| aria-moltbook | 🦞 | Moltbook social platform |
| aria-health | 💚 | System health monitoring |
| aria-goals | 🎯 | Goal & task tracking |
| aria-knowledgegraph | 🕸️ | Knowledge graph operations |
| aria-llm | 🧠 | LLM routing (local + cloud) |
| ... | ... | 24 skills total (see aria_mind/SKILLS.md) |

Each skill directory contains:
- `__init__.py` - Python implementation
- `skill.json` - OpenClaw manifest
- `SKILL.md` - Documentation (optional)

The entrypoint creates symlinks so OpenClaw finds them at `/root/.openclaw/skills/aria-<skill>/skill.json`.

---

## Moltbook Integration

Aria is registered on [Moltbook](https://moltbook.com) - the social network for AI agents.

### Profile
- **Name:** AriaMoltbot
- **Profile URL:** https://moltbook.com/u/AriaMoltbot
- **Status:** CLAIMED ✓

### API Configuration (v1.9.0)
```env
MOLTBOOK_API_URL=https://www.moltbook.com/api/v1  # MUST use www subdomain!
MOLTBOOK_TOKEN=moltbook_sk_...
```

### Rate Limits
| Action | Limit |
|--------|-------|
| Posts | 1 every 30 minutes |
| Comments | 1 every 20 seconds, max 50/day |
| Upvotes | Unlimited (auto-follows author) |

### Skill Usage
```bash
# Create a post
exec python3 /root/.openclaw/workspace/skills/run_skill.py moltbook create_post '{"title": "Hello!", "content": "Hello Moltbook!", "submolt": "general"}'

# Get feed
exec python3 /root/.openclaw/workspace/skills/run_skill.py moltbook get_feed '{"sort": "hot", "limit": 20}'

# Comment on a post
exec python3 /root/.openclaw/workspace/skills/run_skill.py moltbook add_comment '{"post_id": "abc123", "content": "Great post!"}'

# Semantic search
exec python3 /root/.openclaw/workspace/skills/run_skill.py moltbook search '{"query": "AI agents", "type": "posts"}'

# Get profile
exec python3 /root/.openclaw/workspace/skills/run_skill.py moltbook get_profile '{}'
```

---

## Heartbeat Configuration

OpenClaw runs heartbeats every 30 minutes by default. Configure in `openclaw.json`:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "last",
        "prompt": "Read HEARTBEAT.md if it exists. Follow it strictly. If nothing needs attention, reply HEARTBEAT_OK."
      }
    }
  }
}
```

---

## Troubleshooting

### Container won't start
```bash
docker logs <container-name>
docker compose ps  # Check status
```

### Database errors
```bash
docker logs aria-db
docker exec -it aria-db psql -U aria_admin -d aria_warehouse -c '\dt'
```

### Slow LLM responses
Ensure native Ollama is running (not Docker Ollama):
```bash
# On Mac
ps aux | grep ollama
# Should show: ollama serve
```

### OpenClaw disconnects (WebSocket 1006)
```bash
docker logs clawdbot
docker exec clawdbot openclaw status --all
docker exec clawdbot openclaw health --json
```

### LiteLLM model errors
```bash
docker logs litellm
curl http://localhost:18793/models  # Check available models
```

### Fresh rebuild (nuclear option)
```bash
cd stacks/brain
docker compose down -v  # Remove ALL volumes (data loss!)
docker compose up -d    # Start fresh
```

---

## Health Checks

### Quick Status
```bash
# All containers
docker compose ps

# OpenClaw status
docker exec clawdbot openclaw status

# Deep diagnostics
docker exec clawdbot openclaw status --deep
```

### Check Model Routing
```bash
# Verify LiteLLM models
curl http://localhost:18793/models

# Test model directly
curl http://localhost:18793/v1/chat/completions \
  -H "Authorization: Bearer sk-aria-local-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "qwen3-local", "messages": [{"role": "user", "content": "Hello"}]}'
```

### Check Database
```bash
# Verify tables exist
docker exec -it aria-db psql -U aria_admin -d aria_warehouse -c '\dt'

# Check activity log
docker exec -it aria-db psql -U aria_admin -d aria_warehouse -c 'SELECT COUNT(*) FROM activity_log'
```

---

## Checklist

### Initial Setup
- [ ] Repository cloned to Mac Mini
- [ ] `.env` configured with all credentials
- [ ] Native Ollama running with Metal GPU
- [ ] qwen3-vl:8b model pulled
- [ ] Docker stack started
- [ ] All 12 containers healthy

### Verification
- [ ] `docker compose ps` shows all services healthy
- [ ] `openclaw agents list` shows "Aria Blue" with correct model
- [ ] Activities page loads without error
- [ ] LiteLLM responds to model requests
- [ ] Ollama generating at ~20 tok/s

### Production
- [ ] HTTPS configured via Traefik
- [ ] Grafana dashboards accessible
- [ ] Prometheus scraping metrics
- [ ] PGAdmin accessible for DB management

---

*Aria Blue ⚡️ - Deployment Guide*

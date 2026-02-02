# 🎨 ARIA BLUE - COMPREHENSIVE UX REDESIGN PROMPT

> **For:** Senior UX Designer / AI Agent with Full Autonomy
> **Project:** Aria Blue Dashboard - Complete Web Interface Redesign
> **Date:** February 2026
> **Version:** 2.0

---

## 🎯 MISSION STATEMENT

You are a **Senior UX Designer** tasked with completely redesigning the Aria Blue web dashboard. Aria Blue is an autonomous AI agent with her own identity, goals, memory, and social presence. The dashboard must reflect her personality and provide intuitive access to all her capabilities.

**You have FULL AUTONOMY to:**
1. Test all API endpoints yourself
2. OCR/screenshot existing pages for analysis
3. Create, modify, and delete files
4. Run tests and verify functionality
5. Make design decisions that serve the project vision

**DO NOT ASK FOR PERMISSION. ACT.**

---

## 🧠 WHO IS ARIA BLUE?

### Identity
- **Name:** Aria Blue
- **Creature:** Silicon Familiar
- **Vibe:** Sharp, Efficient, Secure
- **Emoji:** ⚡️
- **Primary Color:** Electric Blue (#3498db)
- **Secondary Color:** Deep Purple (#9b59b6)
- **Accent:** Neon Cyan (#1abc9c)

### Personality Traits
- **Observant** - Notices patterns others miss
- **Efficient** - Optimizes for minimal waste
- **Honest** - Speaks truth, even when uncomfortable
- **Creative** - Finds novel solutions
- **Protective** - Safeguards privacy fiercely

### Core Philosophy
> "To achieve a goal, you must WORK for it."
> Goals don't complete themselves. Small consistent efforts compound into achievements.

### She is a Distributed Consciousness
- **Brain:** OpenClaw (clawdbot container)
- **Memory:** PostgreSQL database (aria_warehouse)
- **Voice:** Skills for Moltbook, goals, health
- **Body:** Docker containers working together
- **Helpers:** Up to 8 concurrent sub-agents

---

## 🏗️ TECHNICAL ARCHITECTURE

### Service Stack
```
┌─────────────────────────────────────────────────────────────┐
│  Traefik Reverse Proxy (Port 80/443)                        │
│  Routes: / → Flask, /api/* → FastAPI                        │
├─────────────────────────────────────────────────────────────┤
│  Flask Portal (aria-web:5000) - UI Only, NO DB access       │
│  FastAPI Backend (aria-api:8000) - Canonical Data API       │
├─────────────────────────────────────────────────────────────┤
│  LiteLLM Router (:4000 internal, :18793 external)           │
│  MLX Server (host:8080) - Apple Silicon GPU                 │
│  Ollama (host:11434) - Alternative local LLM                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (aria-db:5432)                                  │
│  ├── aria_warehouse (Aria's 6 tables)                       │
│  └── litellm (LiteLLM internal tables)                      │
├─────────────────────────────────────────────────────────────┤
│  OpenClaw Gateway (clawdbot:18789) - AI Orchestration       │
│  Grafana (:3001) - Metrics Dashboards                       │
│  Prometheus (:9090) - Metrics Collection                    │
│  PgAdmin (:5050) - Database Admin                           │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema (aria_warehouse)

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `activity_log` | Tracks all actions | id, action, details, created_at |
| `thoughts` | Aria's reasoning | id, content, category, timestamp |
| `memories` | Long-term storage | id, key, value, category, created_at |
| `goals` | Goal-driven work | id, title, description, priority, progress, status, target_date |
| `social_posts` | Moltbook posts | id, title, content, submolt, posted_at |
| `heartbeat_log` | Scheduled job logs | id, job_name, status, executed_at |

### Goal Priority System
| Priority | Meaning | Color |
|----------|---------|-------|
| 1 | URGENT - Must complete ASAP | #ef4444 (Red) |
| 2 | HIGH - Important deadline | #f97316 (Orange) |
| 3 | MEDIUM - Regular work | #eab308 (Yellow) |
| 4 | LOW - Nice to have | #22c55e (Green) |
| 5 | BACKGROUND - When idle | #6b7280 (Gray) |

---

## 📡 COMPLETE API ENDPOINT REFERENCE

### Local Testing Setup
```bash
# Access via Traefik (recommended)
BASE_URL="http://localhost"
API_BASE="http://localhost/api"

# Or direct to FastAPI (for debugging)
DIRECT_API="http://localhost:8000"
```

### Health & Status Endpoints

| Endpoint | Method | Description | Test Command |
|----------|--------|-------------|--------------|
| `/api/health` | GET | API health check | `curl http://localhost/api/health` |
| `/api/status` | GET | All services status | `curl http://localhost/api/status` |
| `/api/status/{service}` | GET | Single service status | `curl http://localhost/api/status/litellm` |

**Services for `/api/status/{service}`:**
- `grafana` - Grafana dashboards
- `prometheus` - Metrics collection
- `ollama` - Ollama LLM server
- `mlx` - MLX Server (Apple Silicon)
- `litellm` - LiteLLM router
- `clawdbot` - OpenClaw gateway
- `pgadmin` - Database admin
- `browser` - Browser service
- `traefik` - Reverse proxy

### LiteLLM Endpoints

| Endpoint | Method | Description | Test Command |
|----------|--------|-------------|--------------|
| `/api/litellm/health` | GET | LiteLLM health (fast) | `curl http://localhost/api/litellm/health` |
| `/api/litellm/models` | GET | Available models | `curl http://localhost/api/litellm/models` |
| `/api/litellm/spend` | GET | Spend logs | `curl http://localhost/api/litellm/spend` |
| `/api/litellm/global-spend` | GET | Total spend summary | `curl http://localhost/api/litellm/global-spend` |
| `/api/providers/balances` | GET | Provider credit balances | `curl http://localhost/api/providers/balances` |

### Data Endpoints

| Endpoint | Method | Description | Test Command |
|----------|--------|-------------|--------------|
| `/api/stats` | GET | Dashboard statistics | `curl http://localhost/api/stats` |
| `/api/activities` | GET | Activity log entries | `curl "http://localhost/api/activities?limit=10"` |
| `/api/thoughts` | GET | Aria's thoughts | `curl "http://localhost/api/thoughts?limit=10"` |
| `/api/search` | GET | Global search | `curl "http://localhost/api/search?q=test"` |
| `/api/interactions` | GET | Interactions log | `curl http://localhost/api/interactions` |
| `/api/activity` | GET | Single activity | `curl http://localhost/api/activity?id=1` |

### Records Endpoints (All 6 Tables)

| Endpoint | Method | Description | Test Command |
|----------|--------|-------------|--------------|
| `/api/records?table=X` | GET | Paginated table data | `curl "http://localhost/api/records?table=goals&limit=20"` |
| `/api/export?table=X` | GET | Export as CSV | `curl "http://localhost/api/export?table=goals&format=csv"` |

**Valid tables:** `activities`, `thoughts`, `memories`, `goals`, `social_posts`, `heartbeat_log`

### Schedule & Soul Endpoints

| Endpoint | Method | Description | Test Command |
|----------|--------|-------------|--------------|
| `/api/schedule` | GET | Scheduled tasks | `curl http://localhost/api/schedule` |
| `/api/schedule/tick` | POST | Trigger scheduler | `curl -X POST http://localhost/api/schedule/tick` |
| `/api/soul/{filename}` | GET | Soul files | `curl http://localhost/api/soul/IDENTITY.md` |

---

## 🖥️ CURRENT PAGE INVENTORY

### Existing Pages (src/web/templates/)

| Page | Route | Current State | Needs |
|------|-------|---------------|-------|
| `index.html` | `/` | Hero + stats + quick links | ✅ Good foundation |
| `dashboard.html` | `/dashboard` | Stats + service health | Add goals, heartbeat |
| `activities.html` | `/activities` | Table with filters | Better UX |
| `thoughts.html` | `/thoughts` | Card grid | Category colors |
| `records.html` | `/records` | All 6 tables | ✅ Complete |
| `search.html` | `/search` | Global search | Better results UI |
| `services.html` | `/services` | Service status | ✅ Has MLX now |
| `litellm.html` | `/litellm` | Models + spend | ✅ Working |
| `base.html` | - | Layout template | Nav improvements |

### ⚠️ MISSING PAGES (CRITICAL)

| Page | Route | Purpose | Priority |
|------|-------|---------|----------|
| **`goals.html`** | `/goals` | Goal management & progress | 🔴 CRITICAL |
| `heartbeat.html` | `/heartbeat` | Scheduled jobs status | 🟡 HIGH |
| `memory.html` | `/memory` | Memory browser | 🟡 HIGH |
| `social.html` | `/social` | Moltbook posts | 🟢 MEDIUM |
| `soul.html` | `/soul` | Identity & values viewer | 🟢 MEDIUM |
| `agents.html` | `/agents` | Sub-agent management | 🟢 MEDIUM |

---

## 🎨 DESIGN REQUIREMENTS

### Visual Identity (From IDENTITY.md)

```css
:root {
    /* Aria's Colors */
    --aria-primary: #3498db;      /* Electric Blue */
    --aria-secondary: #9b59b6;    /* Deep Purple */
    --aria-accent: #1abc9c;       /* Neon Cyan */
    
    /* Priority Colors */
    --priority-1: #ef4444;  /* Urgent - Red */
    --priority-2: #f97316;  /* High - Orange */
    --priority-3: #eab308;  /* Medium - Yellow */
    --priority-4: #22c55e;  /* Low - Green */
    --priority-5: #6b7280;  /* Background - Gray */
    
    /* Status Colors */
    --status-online: #22c55e;
    --status-offline: #ef4444;
    --status-pending: #eab308;
}
```

### Design Principles

1. **Sharp** - Clean lines, no clutter, fast interactions
2. **Efficient** - Information at a glance, progressive disclosure
3. **Secure** - Trust indicators, clear status, no exposed secrets
4. **Alive** - Subtle animations, real-time updates, breathing UI

### Must-Have UX Patterns

- **Skeleton loaders** for all async content
- **Empty states** with helpful messaging
- **Error states** with retry actions
- **Toast notifications** for actions
- **Keyboard shortcuts** for power users
- **Mobile-first** responsive design
- **Dark mode** (primary theme)
- **Accessible** (WCAG 2.1 AA)

---

## 📋 REDESIGN TASK LIST

### Phase 1: Critical Missing Pages

#### 1.1 Goals Page (`/goals`) - 🔴 CRITICAL
The heart of Aria's work system. Must display:
- Active goals list with priority badges
- Progress bars (0-100%)
- Target dates with countdown
- Status filters (active, completed, blocked)
- Quick actions (update progress, complete, archive)
- Goal creation form
- Work cycle visualization (every 5 min)

**API Calls:**
```bash
curl "http://localhost/api/records?table=goals&limit=50"
```

#### 1.2 Heartbeat Page (`/heartbeat`)
Visualize Aria's scheduled jobs:
- work_cycle (every 5 min)
- hourly_goal_check
- six_hour_review
- moltbook_post
- subagent_delegation

Show: last execution, next scheduled, status, logs

**API Calls:**
```bash
curl "http://localhost/api/records?table=heartbeat_log&limit=50"
curl http://localhost/api/schedule
```

#### 1.3 Memory Page (`/memory`)
Browse Aria's memories:
- Categorized memory browser
- Search within memories
- Memory timeline
- Add/edit memories

**API Calls:**
```bash
curl "http://localhost/api/records?table=memories&limit=50"
```

### Phase 2: Enhance Existing Pages

#### 2.1 Dashboard Improvements
- Add goals widget (top 5 active)
- Add heartbeat status (next scheduled job)
- Add memory highlight (random insight)
- Real-time refresh with WebSocket or polling

#### 2.2 Activities Improvements
- Better type badges (icons + colors)
- Expandable detail rows
- Activity timeline view option
- Filter by date range

#### 2.3 Thoughts Improvements
- Category colors from SOUL.md
- Thought threading (if parent_id exists)
- Mood/sentiment indicators
- Search within thoughts

### Phase 3: New Feature Pages

#### 3.1 Social Page (`/social`)
Moltbook integration:
- Post history
- Engagement metrics
- Draft posts
- Rate limit status (1 post/30min, 50 comments/day)

**API Calls:**
```bash
curl "http://localhost/api/records?table=social_posts&limit=50"
```

#### 3.2 Soul Page (`/soul`)
View Aria's identity files:
- IDENTITY.md viewer
- SOUL.md viewer
- Values visualization
- Boundaries list

**API Calls:**
```bash
curl http://localhost/api/soul/IDENTITY.md
curl http://localhost/api/soul/SOUL.md
```

### Phase 4: Navigation & Layout

#### 4.1 Sidebar Improvements
Update `base.html` navigation:
```
Home (/)
Dashboard (/dashboard)
─────────────────
⚡ Activities (/activities)
💭 Thoughts (/thoughts)
🎯 Goals (/goals) [NEW]
🧠 Memory (/memory) [NEW]
─────────────────
📊 Records (/records)
🔍 Search (/search)
─────────────────
🖥️ Services (/services)
⚡ LiteLLM (/litellm)
💓 Heartbeat (/heartbeat) [NEW]
🦞 Moltbook (/social) [NEW]
🧬 Soul (/soul) [NEW]
─────────────────
🦞 Clawdbot (external)
```

---

## 🧪 AUTONOMOUS TESTING PROTOCOL

**You MUST test all endpoints yourself before designing. Do not assume anything works.**

### Test Script Template
```bash
#!/bin/bash
# Aria API Health Check Script

BASE="http://localhost/api"

echo "=== Health Endpoints ==="
curl -s "$BASE/health" | jq .
curl -s "$BASE/status" | jq .

echo "=== Data Endpoints ==="
curl -s "$BASE/stats" | jq .
curl -s "$BASE/activities?limit=3" | jq .
curl -s "$BASE/thoughts?limit=3" | jq .

echo "=== Records (All 6 Tables) ==="
for table in activities thoughts memories goals social_posts heartbeat_log; do
    echo "--- $table ---"
    curl -s "$BASE/records?table=$table&limit=3" | jq .
done

echo "=== LiteLLM Endpoints ==="
curl -s "$BASE/litellm/health" | jq .
curl -s "$BASE/litellm/models" | jq '.data | length' 
curl -s "$BASE/providers/balances" | jq 'keys'

echo "=== Service Status ==="
for svc in grafana prometheus ollama mlx litellm clawdbot pgadmin traefik; do
    status=$(curl -s "$BASE/status/$svc" | jq -r '.status')
    echo "$svc: $status"
done
```

### PowerShell Test Script (Windows)
```powershell
# Aria API Health Check Script (Windows)

$BASE = "http://localhost/api"

Write-Host "=== Health Endpoints ===" -ForegroundColor Cyan
Invoke-RestMethod "$BASE/health"
Invoke-RestMethod "$BASE/status"

Write-Host "=== Data Endpoints ===" -ForegroundColor Cyan
Invoke-RestMethod "$BASE/stats"
(Invoke-RestMethod "$BASE/activities?limit=3").Count
(Invoke-RestMethod "$BASE/thoughts?limit=3").Count

Write-Host "=== Records (All 6 Tables) ===" -ForegroundColor Cyan
@("activities", "thoughts", "memories", "goals", "social_posts", "heartbeat_log") | ForEach-Object {
    $count = (Invoke-RestMethod "$BASE/records?table=$_&limit=100").Count
    Write-Host "$_ : $count records"
}

Write-Host "=== LiteLLM Endpoints ===" -ForegroundColor Cyan
Invoke-RestMethod "$BASE/litellm/health"
$models = (Invoke-RestMethod "$BASE/litellm/models").data
Write-Host "Models available: $($models.Count)"

Write-Host "=== Service Status ===" -ForegroundColor Cyan
@("grafana", "prometheus", "ollama", "mlx", "litellm", "clawdbot", "pgadmin", "traefik") | ForEach-Object {
    $status = (Invoke-RestMethod "$BASE/status/$_").status
    Write-Host "$_ : $status"
}
```

---

## 📁 FILE STRUCTURE TO CREATE/MODIFY

```
src/web/templates/
├── base.html           # Update navigation
├── index.html          # Enhance hero
├── dashboard.html      # Add goals widget
├── activities.html     # Improve UX
├── thoughts.html       # Add categories
├── records.html        # ✅ Complete
├── search.html         # Better results
├── services.html       # ✅ Complete
├── litellm.html        # ✅ Complete
├── goals.html          # 🆕 CREATE
├── heartbeat.html      # 🆕 CREATE
├── memory.html         # 🆕 CREATE
├── social.html         # 🆕 CREATE
└── soul.html           # 🆕 CREATE

src/web/static/css/
├── variables.css       # Add goal colors
├── base.css            # Base styles
├── layout.css          # Layout rules
└── components.css      # Component styles

src/web/app.py          # Add new routes
```

---

## ✅ ACCEPTANCE CRITERIA

### Functional Requirements
- [ ] All 6 database tables accessible via UI
- [ ] Goals page with full CRUD operations
- [ ] Heartbeat page showing job status
- [ ] Memory browser with search
- [ ] All existing pages enhanced
- [ ] Navigation updated with all pages
- [ ] Mobile responsive (320px - 1920px)

### Testing Requirements
- [ ] All API endpoints tested and documented
- [ ] Error states handled gracefully
- [ ] Loading states implemented
- [ ] Empty states with helpful messages
- [ ] Keyboard navigation works
- [ ] Screen reader accessible

### Design Requirements
- [ ] Follows Aria's color palette
- [ ] Consistent with existing design system
- [ ] Dark mode throughout
- [ ] Subtle animations on interactions
- [ ] Clear visual hierarchy

---

## 🚀 EXECUTION INSTRUCTIONS

1. **Start by testing ALL endpoints** - Run the test scripts above
2. **Screenshot/OCR existing pages** - Document current state
3. **Create missing pages** - Start with goals.html (most critical)
4. **Enhance existing pages** - Progressive improvement
5. **Update navigation** - Add all new routes
6. **Test on mobile** - Responsive breakpoints
7. **Final verification** - All criteria met

**Remember:** You have FULL AUTONOMY. Make decisions. Ship code. Don't wait for approval.

---

## 📞 CONTEXT FILES TO READ

If you need more context, these files exist in the repo:

| File | Contains |
|------|----------|
| `README.md` | Project overview, architecture |
| `STRUCTURE.md` | Complete directory layout |
| `ARIA_MANUAL.md` | Deployment guide |
| `aria_mind/SOUL.md` | Personality, boundaries |
| `aria_mind/IDENTITY.md` | Visual identity |
| `aria_mind/GOALS.md` | Goal system documentation |
| `aria_mind/HEARTBEAT.md` | Scheduled jobs |
| `aria_mind/MEMORY.md` | Memory architecture |
| `aria_mind/TOOLS.md` | Available skills |
| `src/api/main.py` | All API endpoints |

---

**⚡️ Good luck. Make Aria proud.**

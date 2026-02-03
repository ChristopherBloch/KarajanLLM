# Aria Codebase Optimization Review

**Date:** 2026-02-03  
**Reviewer:** Copilot Code Review  
**Status:** ✅ IMPLEMENTED

---

## Current Task: Unify API Architecture

### Goal
All Aria skills MUST use the AriaAPIClient to interact with data. No direct database access from skills. Single source of truth: `src/api/main.py`.

### Architecture
```
┌─────────────────┐     ┌─────────────────┐
│   aria-web      │────▶│   aria-api      │
│   (Flask)       │     │   (FastAPI)     │
│   Port 5000     │     │   Port 8000     │
└─────────────────┘     └────────┬────────┘
                                 │
┌─────────────────┐              │
│   aria_skills   │──────────────┤
│   (via API)     │              │
└─────────────────┘              ▼
                        ┌─────────────────┐
                        │   aria-db       │
                        │   (PostgreSQL)  │
                        │   Port 5432     │
                        └─────────────────┘
```

### Phase 1: Refactor Skills to Use API Client
- [x] 1.1 Update `knowledge_graph.py` - Remove asyncpg, use AriaAPIClient
- [x] 1.2 Update `goals.py` - Add API persistence via AriaAPIClient  
- [x] 1.3 Update `social.py` - Use AriaAPIClient for posts
- [x] 1.4 Update `performance.py` - Use AriaAPIClient for logs
- [ ] 1.5 Keep `database.py` as low-level fallback only (not used by other skills)

### Phase 2: Testing
- [x] 2.1 Add pytest tests for AriaAPIClient
- [ ] 2.2 Test each refactored skill
- [ ] 2.3 Integration test: skill → API → DB → response

### Phase 3: Deploy & Verify
- [ ] 3.1 Commit and push
- [ ] 3.2 Run full test suite on server
- [ ] 3.3 Run integration tests on server
- [ ] 3.4 Rebuild containers (deploy)

### Phase 4: Integration Audit
- [ ] 4.1 Verify aria_skills use AriaAPIClient (no direct DB access)
- [ ] 4.2 Verify openclaw_skills manifests match aria_skills classes
- [ ] 4.3 Update any mismatches
- [ ] 4.4 Report gaps and required follow-ups

---

## Current Task: Centralize Model Catalog

### Goal
Create a single source of truth for model definitions and routing criteria in `aria_models/`, then reference it from config generation and code paths that currently hardcode model lists.

### Phase 1: Plan & Design
- [x] 1.1 Inventory all model references and classify by usage (routing, UI, docs, tests)
- [x] 1.2 Define YAML schema (models, providers, criteria/top lists, aliases)
- [x] 1.3 Identify minimal code paths to consume YAML first (openclaw config + model selection)

### Phase 2: Implement
- [x] 2.1 Create `aria_models/models.yaml` with current model set and criteria lists
- [x] 2.2 Add loader module to read YAML and expose helpers
- [x] 2.3 Update openclaw config generation / model routing to use YAML
- [x] 2.4 Update references in coordinator/model selection to use YAML

### Phase 3: Docs & Verification
- [x] 3.1 Update model documentation to reference YAML (single source of truth)
- [ ] 3.2 Run tests relevant to model selection/config
- [ ] 3.3 Add review notes

---

## Current Task: Service Controls (Host + Docker)

### Goal
Make kill/restart buttons work for Docker services and host services (MLX/Ollama) without hardcoding secrets.

### Phase 1: Plan & Design
- [ ] 1.1 Add host-control path via SSH helper (no secrets in repo)
- [ ] 1.2 Add env placeholders and compose mount for host SSH keys
- [ ] 1.3 Update docs/notes for safe setup

### Phase 2: Implement
- [ ] 2.1 Add host command execution in API (launchctl via SSH)
- [ ] 2.2 Update Dockerfile to include SSH client
- [ ] 2.3 Update docker-compose + .env placeholders

### Phase 3: Verify
- [ ] 3.1 Manual API call for host service action
- [ ] 3.2 Confirm UI action behavior

---

## Previous Changes Applied

### Architecture Consolidation
- [x] Created [ARIA.md](../aria_mind/ARIA.md) - Lean system prompt (~60 lines vs 400+ combined)
- [x] Streamlined [TOOLS.md](../aria_mind/TOOLS.md) - Now 60 lines vs 376 (skills in openclaw_skills/*.json)
- [x] Streamlined [AWAKENING.md](../aria_mind/AWAKENING.md) - Clean startup protocol
- [x] Removed duplicate files: FOCUSES.md, IDENTITY.md, SOUL.md (Python files are source of truth)

### Critical Fixes Applied
- [x] Added error handling to LLM calls in [coordinator.py](../aria_agents/coordinator.py#L65-L80)
- [x] Fixed heartbeat task cancellation in [heartbeat.py](../aria_mind/heartbeat.py#L57-L66)
- [x] Added parallel broadcast in [coordinator.py](../aria_agents/coordinator.py#L201-L225)

### Performance Optimizations
- [x] Pre-compiled regex patterns in [boundaries.py](../aria_mind/soul/boundaries.py#L10-L17)
- [x] Replaced list with deque in [memory.py](../aria_mind/memory.py#L6-L27)

---

## Token Savings Summary

| File | Before | After | Saved |
|------|--------|-------|-------|
| TOOLS.md | 376 lines | 60 lines | 316 |
| AWAKENING.md | 180 lines | 55 lines | 125 |
| SOUL.md | 110 lines | Deleted | 110 |
| IDENTITY.md | 80 lines | Deleted | 80 |
| FOCUSES.md | 274 lines | Deleted | 274 |
| NEW: ARIA.md | - | 60 lines | (combined) |
| **Total** | ~1020 | ~175 | **~845 lines** |

---

## Remaining Recommendations (Backlog)

### Medium Priority
- [ ] Remove unused imports across modules
- [ ] Create `BaseAPISkill` for HTTP client deduplication
- [ ] Create `SessionManagerMixin` for session handling
- [ ] Add `is_available` checks to 8 skills
- [ ] Standardize logger usage (self.logger vs module-level)

### Low Priority
- [ ] HTTP connection pooling
- [ ] Externalize config to YAML
- [ ] Remove dead factory functions
- [ ] Type annotation consistency

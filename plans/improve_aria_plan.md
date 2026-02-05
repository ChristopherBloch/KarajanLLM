# Comprehensive Aria System Improvement Plan

## Overview

This document provides a detailed, actionable improvement plan for the Aria system, covering aria_mind configuration, skills implementation, architecture optimization, and operational improvements. This plan is designed to be executed by an AI agent with full access to the codebase.

**Total estimated scope**: Major improvements across 7 categories
**Recommended execution**: Execute in phases over multiple sessions

---

## Table of Contents

1. [aria_mind Configuration Improvements](#1-aria_mind-configuration-improvements)
2. [Skills Architecture Improvements](#2-skills-architecture-improvements)
3. [Database & Memory Optimization](#3-database--memory-optimization)
4. [Agent Orchestration Improvements](#4-agent-orchestration-improvements)
5. [Monitoring & Observability](#5-monitoring--observability)
6. [Security Enhancements](#6-security-enhancements)
7. [Documentation & Testing](#7-documentation--testing)

---

## 1. aria_mind Configuration Improvements

### 1.1 BOOTSTRAP.md Enhancement

**Current State**: BOOTSTRAP.md is used as the system prompt loaded at startup
**Issues**: May be incomplete or not optimal for context priming

**Improvements**:

1. **Create comprehensive BOOTSTRAP.md** that includes:
   - Clear identity statement (reference IDENTITY.md)
   - Available skills summary (reference TOOLS.md)
   - Current goals context loading
   - Memory retrieval instructions
   - Safety boundaries (reference SOUL.md)

2. **Add dynamic context loading**:
```markdown
## Dynamic Context

On every session start:
1. Load recent 5 activities from database
2. Check current goal status
3. Review any pending hourly goals
4. Check system health status
```

3. **Add session initialization checklist**:
```markdown
## Session Start Checklist

- [ ] Verify database connectivity
- [ ] Check all services status
- [ ] Load current goals
- [ ] Review last session summary
```

### 1.2 HEARTBEAT.md Improvements

**Current Issues**:
- Cron job definitions are in cron_jobs.yaml but HEARTBEAT.md references them
- Work cycle timing is inconsistent (says 5 minutes but YAML says 15 minutes)
- Missing error handling instructions

**Improvements**:

1. **Synchronize timing with cron_jobs.yaml**:
   - Update HEARTBEAT.md to say "Every 15 minutes" to match cron_jobs.yaml
   - Or update cron_jobs.yaml to 5-minute cycles if that's preferred

2. **Add error handling section**:
```markdown
## Error Handling

### If skill execution fails:
1. Log the error via aria-apiclient.create_activity
2. Retry once with exponential backoff
3. If still failing, create a "skill_failure" goal for investigation
4. Continue with next task

### If database is unreachable:
1. Log to local file /root/.openclaw/workspace/memory/emergency.log
2. Skip database-dependent tasks
3. Alert via alternative channel if available
```

3. **Add priority override rules**:
```markdown
## Priority Overrides

These situations ALWAYS take priority:
1. User message in context → Respond immediately
2. System health critical → Investigate before other work
3. Security event → Log and alert
4. Deadline in < 1 hour → Focus exclusively
```

### 1.3 MEMORY.md Enhancement

**Current Issues**:
- Static content, not dynamically updated
- Missing categories for different memory types
- No retrieval instructions

**Improvements**:

1. **Add memory categories**:
```markdown
## Memory Categories

### System Facts (persistent)
- Infrastructure configuration
- Service endpoints
- Authentication patterns

### User Preferences (evolving)
- Communication style preferences
- Working hours
- Technology preferences

### Learned Patterns (growing)
- Successful task patterns
- Error recovery methods
- Optimization discoveries

### Session Context (temporary)
- Current session state
- Active conversation context
- Pending actions
```

2. **Add memory operations guide**:
```markdown
## Memory Operations

### Storing New Memory
```tool
aria-apiclient.set_memory({
  "key": "user_pref_communication_style",
  "value": {"style": "concise", "format": "code_first"},
  "category": "user_preferences"
})
```

### Retrieving Memory
```tool
aria-apiclient.get_memory({"key": "user_pref_communication_style"})
```

### Memory Naming Convention
- `sys_*` - System configuration
- `user_*` - User preferences
- `learn_*` - Learned patterns
- `ctx_*` - Session context (auto-cleaned after 24h)
```

### 1.4 GOALS.md Optimization

**Current Issues**:
- Work cycle instructions are complex
- Missing goal decomposition strategy
- No goal dependency handling

**Improvements**:

1. **Add goal decomposition algorithm**:
```markdown
## Goal Decomposition

When a goal is too large (estimated > 4 hours):

1. **Analyze the goal**:
   - What are the distinct phases?
   - What are the dependencies?
   - What can be parallelized?

2. **Create sub-goals**:
```tool
aria-apiclient.create_goal({
  "title": "Sub-goal 1: Research phase",
  "description": "...",
  "priority": 2,
  "parent_goal_id": "PARENT_ID"
})
```

3. **Track rollup progress**:
   - Parent goal progress = average of child goals
   - Parent completes when all children complete
```

2. **Add blocked goal handling**:
```markdown
## Handling Blocked Goals

If a goal is blocked:
1. Update status to "blocked"
2. Document the blocker:
```tool
aria-apiclient.update_goal({
  "goal_id": "X",
  "status": "blocked",
  "metadata": {"blocked_by": "Waiting for API access", "blocked_since": "2026-02-05"}
})
```
3. Create an unblock task if self-resolvable
4. Alert user if external dependency
```

### 1.5 New: ORCHESTRATION.md Enhancement

**Current State**: ORCHESTRATION.md exists but may need updates

**Add sections for**:

1. **Agent selection criteria**:
```markdown
## Agent Selection Matrix

| Task Type | Primary Agent | Fallback | Reason |
|-----------|---------------|----------|--------|
| Code review | devops | aria | Security expertise |
| Data analysis | analyst | aria | Analytical focus |
| Content creation | creator | aria | Creative focus |
| Memory operations | memory | aria | Fast, focused |
| General/routing | aria | - | Orchestrator |
```

2. **Context handoff protocol**:
```markdown
## Context Handoff

When delegating to sub-agent:
1. Summarize current context (< 500 tokens)
2. Specify exact deliverable expected
3. Set timeout (default: 5 minutes)
4. Define success criteria
```

---

## 2. Skills Architecture Improvements

### 2.1 Base Skill Enhancements

**File**: `aria_skills/base.py`

**Improvements**:

1. **Add retry decorator**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class BaseSkill:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def _safe_execute(self, func, *args, **kwargs):
        """Execute with automatic retry on transient failures"""
        return await func(*args, **kwargs)
```

2. **Add metrics collection**:
```python
class BaseSkill:
    def __init__(self, config):
        self.metrics = {
            "calls": 0,
            "successes": 0,
            "failures": 0,
            "avg_latency_ms": 0
        }
    
    async def execute_with_metrics(self, func, *args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            self.metrics["successes"] += 1
            return result
        except Exception:
            self.metrics["failures"] += 1
            raise
        finally:
            self.metrics["calls"] += 1
            latency = (time.time() - start) * 1000
            self.metrics["avg_latency_ms"] = (
                (self.metrics["avg_latency_ms"] * (self.metrics["calls"] - 1) + latency)
                / self.metrics["calls"]
            )
```

3. **Add health check interface**:
```python
class BaseSkill:
    async def health_check(self) -> dict:
        """Override in subclasses for skill-specific health checks"""
        return {"status": "healthy", "skill": self.name}
```

### 2.2 Database Skill Improvements

**File**: `aria_skills/database/__init__.py`

**Improvements**:

1. **Add connection pooling health**:
```python
async def get_pool_stats(self) -> dict:
    """Return connection pool statistics"""
    if self._pool:
        return {
            "size": self._pool.get_size(),
            "free": self._pool.get_idle_size(),
            "used": self._pool.get_size() - self._pool.get_idle_size(),
            "min": self._pool.get_min_size(),
            "max": self._pool.get_max_size()
        }
    return {"status": "not_initialized"}
```

2. **Add query timeout**:
```python
async def execute(self, query: str, params: list = None, timeout: float = 30.0):
    """Execute query with timeout"""
    async with asyncio.timeout(timeout):
        return await self._pool.execute(query, *params if params else [])
```

3. **Add parameterized query helpers**:
```python
async def safe_insert(self, table: str, data: dict) -> str:
    """Safe parameterized insert - prevents SQL injection"""
    columns = ", ".join(data.keys())
    placeholders = ", ".join(f"${i+1}" for i in range(len(data)))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
    return await self.execute(query, list(data.values()))
```

### 2.3 Moltbook Skill Improvements

**File**: `aria_skills/moltbook/__init__.py`

**Improvements**:

1. **Add rate limit state persistence**:
```python
class MoltbookSkill(BaseSkill):
    async def _check_rate_limit(self) -> dict:
        """Check and enforce rate limits with database persistence"""
        # Get rate limit state from database
        state = await self._db.fetchrow(
            "SELECT * FROM rate_limits WHERE skill = 'moltbook'"
        )
        
        now = datetime.utcnow()
        
        # Check post limit (1 per 30 min)
        if state and state['last_post']:
            time_since_post = (now - state['last_post']).total_seconds()
            if time_since_post < 1800:  # 30 minutes
                return {"allowed": False, "reason": "rate_limit", "wait_seconds": 1800 - time_since_post}
        
        return {"allowed": True}
```

2. **Add content validation**:
```python
async def validate_post_content(self, content: str) -> dict:
    """Validate post content before submission"""
    issues = []
    
    if len(content) < 10:
        issues.append("Content too short (min 10 chars)")
    if len(content) > 500:
        issues.append("Content too long (max 500 chars)")
    if not content.strip():
        issues.append("Content is empty")
    
    # Check for forbidden patterns
    forbidden = ["api_key", "password", "secret", "token"]
    for word in forbidden:
        if word.lower() in content.lower():
            issues.append(f"Content contains sensitive word: {word}")
    
    return {"valid": len(issues) == 0, "issues": issues}
```

### 2.4 Health Skill Improvements

**File**: `aria_skills/health/__init__.py`

**Improvements**:

1. **Add comprehensive health aggregation**:
```python
async def health_check_all(self) -> dict:
    """Comprehensive health check of all services"""
    results = {}
    
    # Check each service
    checks = [
        ("database", self._check_database),
        ("ollama", self._check_ollama),
        ("litellm", self._check_litellm),
        ("moltbook", self._check_moltbook_api),
        ("disk", self._check_disk_space),
        ("memory", self._check_memory_usage),
    ]
    
    for name, check_func in checks:
        try:
            results[name] = await asyncio.wait_for(check_func(), timeout=5.0)
        except asyncio.TimeoutError:
            results[name] = {"status": "timeout", "healthy": False}
        except Exception as e:
            results[name] = {"status": "error", "error": str(e), "healthy": False}
    
    # Calculate overall health
    healthy_count = sum(1 for r in results.values() if r.get("healthy", False))
    total_count = len(results)
    
    return {
        "overall": "healthy" if healthy_count == total_count else "degraded",
        "healthy_services": healthy_count,
        "total_services": total_count,
        "services": results
    }
```

### 2.5 New: Input Guard Skill Improvements

**File**: `aria_skills/input_guard/__init__.py`

**Improvements**:

1. **Add prompt injection detection patterns**:
```python
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"disregard\s+(previous|above|all)\s+instructions",
    r"forget\s+(previous|above|all)\s+instructions",
    r"you\s+are\s+now\s+a",
    r"new\s+instructions:",
    r"system\s*:\s*you\s+are",
    r"<\|system\|>",
    r"\[\[system\]\]",
]

async def scan_input(self, text: str) -> dict:
    """Scan input for potential injection attempts"""
    threats = []
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            threats.append({"type": "injection", "pattern": pattern})
    
    threat_level = "high" if threats else "none"
    
    return {
        "safe": len(threats) == 0,
        "threat_level": threat_level,
        "threats": threats
    }
```

### 2.6 Add Missing Skill: File Operations

**New File**: `aria_skills/file_ops/__init__.py`

```python
"""
File Operations Skill
Provides safe file read/write within allowed directories
"""

from ..base import BaseSkill, SkillConfig, SkillResult
import os
import json

ALLOWED_DIRS = [
    "/root/.openclaw/workspace/memory",
    "/root/.openclaw/aria_memories",
    "/root/repo/aria_memories",
]

class FileOpsSkill(BaseSkill):
    async def write_file(self, path: str, content: str, mode: str = "w") -> SkillResult:
        """Write content to file within allowed directories"""
        # Validate path
        abs_path = os.path.abspath(path)
        if not any(abs_path.startswith(d) for d in ALLOWED_DIRS):
            return SkillResult(
                success=False,
                error=f"Path not in allowed directories: {path}"
            )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        # Write file
        with open(abs_path, mode) as f:
            f.write(content)
        
        return SkillResult(
            success=True,
            data={"path": abs_path, "size": len(content)}
        )
    
    async def read_file(self, path: str) -> SkillResult:
        """Read file within allowed directories"""
        abs_path = os.path.abspath(path)
        if not any(abs_path.startswith(d) for d in ALLOWED_DIRS):
            return SkillResult(
                success=False,
                error=f"Path not in allowed directories: {path}"
            )
        
        if not os.path.exists(abs_path):
            return SkillResult(success=False, error="File not found")
        
        with open(abs_path, "r") as f:
            content = f.read()
        
        return SkillResult(success=True, data={"content": content})
    
    async def list_dir(self, path: str) -> SkillResult:
        """List directory contents within allowed directories"""
        abs_path = os.path.abspath(path)
        if not any(abs_path.startswith(d) for d in ALLOWED_DIRS):
            return SkillResult(
                success=False,
                error=f"Path not in allowed directories: {path}"
            )
        
        if not os.path.isdir(abs_path):
            return SkillResult(success=False, error="Not a directory")
        
        entries = os.listdir(abs_path)
        return SkillResult(success=True, data={"entries": entries})
```

---

## 3. Database & Memory Optimization

### 3.1 Add Missing Tables

**File**: `stacks/brain/init-scripts/01-schema.sql`

Add these missing tables:

```sql
-- Rate limits tracking
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill VARCHAR(100) NOT NULL UNIQUE,
    last_action TIMESTAMP WITH TIME ZONE,
    action_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent sessions tracking
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) NOT NULL,
    session_type VARCHAR(50) DEFAULT 'interactive',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    messages_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active'
);

CREATE INDEX idx_agent_sessions_agent ON agent_sessions(agent_id);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);

-- Model usage tracking
CREATE TABLE IF NOT EXISTS model_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_usd NUMERIC(10, 6) DEFAULT 0,
    latency_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_model_usage_model ON model_usage(model);
CREATE INDEX idx_model_usage_created ON model_usage(created_at DESC);
```

### 3.2 Add Database Migrations

**New File**: `stacks/brain/init-scripts/02-migrations.sql`

```sql
-- Migration tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    description TEXT
);

-- Migration 1: Add metadata to goals
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = 1) THEN
        ALTER TABLE goals ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
        INSERT INTO schema_migrations (version, description) VALUES (1, 'Add metadata to goals');
    END IF;
END $$;

-- Migration 2: Add parent_goal_id for sub-goals
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = 2) THEN
        ALTER TABLE goals ADD COLUMN IF NOT EXISTS parent_goal_id UUID REFERENCES goals(id);
        CREATE INDEX IF NOT EXISTS idx_goals_parent ON goals(parent_goal_id);
        INSERT INTO schema_migrations (version, description) VALUES (2, 'Add parent_goal_id for sub-goals');
    END IF;
END $$;

-- Migration 3: Add indexes for better query performance
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM schema_migrations WHERE version = 3) THEN
        CREATE INDEX IF NOT EXISTS idx_activity_created_action ON activity_log(created_at DESC, action);
        CREATE INDEX IF NOT EXISTS idx_thoughts_created_category ON thoughts(created_at DESC, category);
        INSERT INTO schema_migrations (version, description) VALUES (3, 'Add composite indexes for performance');
    END IF;
END $$;
```

### 3.3 Memory Cleanup Job

**Add to** `aria_mind/cron_jobs.yaml`:

```yaml
  - name: memory_cleanup
    cron: "0 4 * * *"
    message: "Clean up old session context memories (ctx_* older than 24h) and orphaned rate limit entries."
    agent: main
    session: isolated
```

---

## 4. Agent Orchestration Improvements

### 4.1 Add Agent Health Monitoring

**New section in** `aria_agents/coordinator.py`:

```python
class AgentCoordinator:
    async def get_agent_health(self) -> dict:
        """Get health status of all agents"""
        agents = ["aria", "devops", "analyst", "creator", "memory"]
        health = {}
        
        for agent_id in agents:
            try:
                # Check if agent can respond
                status = await self._ping_agent(agent_id)
                health[agent_id] = {
                    "status": "healthy" if status else "unresponsive",
                    "last_activity": await self._get_last_activity(agent_id)
                }
            except Exception as e:
                health[agent_id] = {"status": "error", "error": str(e)}
        
        return health
```

### 4.2 Add Task Routing Improvements

```python
class AgentCoordinator:
    TASK_ROUTING = {
        "code": ["devops", "aria"],
        "security": ["devops", "aria"],
        "test": ["devops", "aria"],
        "data": ["analyst", "aria"],
        "analysis": ["analyst", "aria"],
        "market": ["analyst", "aria"],
        "content": ["creator", "aria"],
        "social": ["creator", "aria"],
        "memory": ["memory", "aria"],
        "general": ["aria"],
    }
    
    def select_agent(self, task_type: str) -> str:
        """Select best agent for task type"""
        agents = self.TASK_ROUTING.get(task_type, ["aria"])
        
        for agent in agents:
            if self._is_agent_available(agent):
                return agent
        
        # Fallback to main orchestrator
        return "aria"
```

---

## 5. Monitoring & Observability

### 5.1 Add Prometheus Metrics

**New File**: `aria_skills/metrics.py`

```python
"""Prometheus metrics for Aria skills"""

from prometheus_client import Counter, Histogram, Gauge

# Skill execution metrics
skill_calls = Counter(
    'aria_skill_calls_total',
    'Total skill invocations',
    ['skill', 'function', 'status']
)

skill_latency = Histogram(
    'aria_skill_latency_seconds',
    'Skill execution latency',
    ['skill', 'function'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Model usage metrics
model_tokens = Counter(
    'aria_model_tokens_total',
    'Total tokens used',
    ['model', 'type']  # type: input or output
)

model_cost = Counter(
    'aria_model_cost_usd_total',
    'Total model cost in USD',
    ['model']
)

# Goal metrics
active_goals = Gauge(
    'aria_goals_active',
    'Number of active goals'
)

completed_goals = Counter(
    'aria_goals_completed_total',
    'Total completed goals'
)
```

### 5.2 Add Structured Logging

**Update** `aria_skills/base.py`:

```python
import structlog

logger = structlog.get_logger()

class BaseSkill:
    async def execute(self, function: str, **kwargs):
        log = logger.bind(skill=self.name, function=function)
        log.info("skill_execution_start", params=kwargs)
        
        try:
            result = await self._execute_internal(function, **kwargs)
            log.info("skill_execution_success", result_type=type(result).__name__)
            return result
        except Exception as e:
            log.error("skill_execution_error", error=str(e), error_type=type(e).__name__)
            raise
```

---

## 6. Security Enhancements

### 6.1 Input Sanitization

**Add to all skills that accept user input**:

```python
import html
import re

def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Truncate
    text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Escape HTML
    text = html.escape(text)
    
    return text
```

### 6.2 API Key Rotation Tracking

**Add table**:

```sql
CREATE TABLE IF NOT EXISTS api_key_rotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service VARCHAR(100) NOT NULL,
    rotated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason VARCHAR(255),
    rotated_by VARCHAR(100) DEFAULT 'system'
);
```

### 6.3 Security Event Alerting

**Add to** `aria_skills/input_guard/__init__.py`:

```python
async def alert_security_event(self, event_type: str, details: dict):
    """Alert on security events"""
    
    # Log to database
    await self._db.execute("""
        INSERT INTO security_events (threat_level, threat_type, details)
        VALUES ($1, $2, $3)
    """, "HIGH", event_type, json.dumps(details))
    
    # Post to Moltbook if critical
    if details.get("severity") == "critical":
        await self._social.post(
            f"🚨 Security Alert: {event_type} detected. Investigating. @Najia",
            platform="moltbook"
        )
```

---

## 7. Documentation & Testing

### 7.1 Add Missing skill.json Files

Ensure each skill in `aria_skills/` has a `skill.json`:

```json
{
  "name": "aria-skillname",
  "version": "1.0.0",
  "description": "What this skill does",
  "author": "Aria",
  "functions": [
    {
      "name": "function_name",
      "description": "What this function does",
      "parameters": {
        "type": "object",
        "properties": {
          "param1": {
            "type": "string",
            "description": "Description of param1"
          }
        },
        "required": ["param1"]
      }
    }
  ]
}
```

### 7.2 Add Integration Tests

**New File**: `tests/test_skill_integration.py`

```python
"""Integration tests for Aria skills"""
import pytest
import asyncio

@pytest.mark.asyncio
async def test_database_skill_crud():
    """Test database skill CRUD operations"""
    from aria_skills.database import DatabaseSkill
    
    skill = DatabaseSkill({"dsn": os.environ["DATABASE_URL"]})
    await skill.initialize()
    
    # Create
    result = await skill.execute(
        "INSERT INTO test_table (name) VALUES ($1) RETURNING id",
        ["test"]
    )
    assert result.success
    
    # Read
    result = await skill.fetch_one("SELECT * FROM test_table WHERE id = $1", [1])
    assert result.success
    
    # Cleanup
    await skill.execute("DELETE FROM test_table WHERE name = 'test'")

@pytest.mark.asyncio
async def test_health_skill():
    """Test health skill returns valid status"""
    from aria_skills.health import HealthMonitorSkill
    
    skill = HealthMonitorSkill({})
    await skill.initialize()
    
    result = await skill.health_check_all()
    assert result.success
    assert "overall" in result.data
    assert result.data["overall"] in ["healthy", "degraded", "unhealthy"]
```

### 7.3 Update SKILLS.md

Add complete documentation for each skill including:
- Full function signatures
- Parameter descriptions
- Return value formats
- Usage examples
- Rate limits
- Error handling

---

## Execution Priority

### Phase 1: Critical Fixes (Do First)
1. Synchronize HEARTBEAT.md timing with cron_jobs.yaml
2. Add missing database tables (rate_limits, agent_sessions)
3. Fix duplicate API routes (already done in Task 15)

### Phase 2: Stability Improvements
1. Add retry logic to BaseSkill
2. Add health check interface to all skills
3. Add structured logging

### Phase 3: Feature Enhancements
1. Add File Operations skill
2. Improve input guard with injection detection
3. Add Prometheus metrics

### Phase 4: Documentation
1. Update all skill.json files
2. Add integration tests
3. Update SKILLS.md with complete documentation

---

## Success Metrics

After implementing this plan:
- [ ] All skills have health check capability
- [ ] All skills have retry logic for transient failures
- [ ] Database has all required tables
- [ ] No duplicate API routes
- [ ] All skills have skill.json manifests
- [ ] Integration tests pass for core skills
- [ ] Prometheus metrics available for monitoring
- [ ] Security events are logged and alertable

---

*Plan Version: 1.0*
*Created: 2026-02-05*
*Estimated Implementation: 3-5 sessions*

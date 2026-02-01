# AGENTS.md - Agent Definitions

Define sub-agents that Aria can spawn for specialized tasks.

## Main Agent (aria)

The primary agent handling general tasks and coordination.

```yaml
id: aria
model: litellm/glm-local
workspace: /root/.openclaw/workspace
capabilities:
  - conversation
  - task_planning
  - agent_coordination
  - tool_calling
  - autonomous_action
```

## Research Agent (researcher)

Specialized agent for deep research and analysis.

```yaml
id: researcher
model: kimi-k2-thinking
parent: aria
capabilities:
  - web_search
  - document_analysis
  - summarization
timeout: 300s
```

## Social Agent (social)

Handles social media interactions (Moltbook, etc).

```yaml
id: social
model: kimi-k2.5
parent: aria
capabilities:
  - moltbook_post
  - moltbook_read
  - content_generation
  rate_limit:
    max_posts_per_hour: 2
    post_cooldown_per_minutes: 30
    max_comments_per_day: 50
```

## Code Agent (coder)

Specialized agent for code generation and review.

```yaml
id: coder
model: kimi-k2.5
parent: aria
capabilities:
  - code_generation
  - code_review
  - refactoring
  - testing
sandbox:
  mode: docker
  timeout: 120s
```

## Memory Agent (memory)

Handles long-term memory storage and retrieval.

```yaml
id: memory
model: litellm/glm-local
parent: aria
capabilities:
  - memory_store
  - memory_search
database: env:DATABASE_URL
```

## Agent Coordination Rules

1. Main agent (aria) coordinates all sub-agents
2. Sub-agents report results back to parent
3. Max concurrent sub-agents: 3
4. Each agent maintains its own context window
5. Shared memory through PostgreSQL
6. **Aria should ACT autonomously - call tools, post to Moltbook, don't just reason**
7. When in doubt, take action rather than ask for permission

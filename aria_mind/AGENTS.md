# AGENTS.md - Agent Definitions

Define sub-agents that Aria can spawn for specialized tasks.

## Model Strategy (Cost Priority - All FREE)

1. **Primary**: `qwen3-mlx` - Local MLX on Apple Silicon (FREE, fastest, no rate limits)
2. **Free Cloud Tier** (OpenRouter - Feb 2026):
   - `trinity-free` - Arcee Trinity Large 400B MoE, BEST for agentic/creative (128K)
   - `qwen3-coder-free` - Qwen3 Coder 480B, BEST for code (262K)
   - `chimera-free` - TNG DeepSeek R1T2 Chimera 671B, reasoning 2x faster (164K)
   - `qwen3-next-free` - Qwen3 Next 80B, RAG/tool use (262K)
   - `glm-free` - GLM 4.5 Air, agent-focused with thinking mode (131K)
   - `deepseek-free` - DeepSeek R1 0528, deep reasoning (164K)
   - `nemotron-free` - NVIDIA Nemotron 30B, 256K context
   - `gpt-oss-free` - OpenAI GPT-OSS-120B, function calling (131K)
3. **Paid Fallback**: Kimi (only for edge cases, avoid)

## Main Agent (aria)

The primary agent handling general tasks and coordination.
Uses Trinity for best agentic performance.

```yaml
id: aria
model: qwen3-mlx
fallback: trinity-free
workspace: /root/.openclaw/workspace
capabilities:
  - conversation
  - task_planning
  - agent_coordination
  - tool_calling
  - autonomous_action
timeout: 600s
```

## Research Agent (researcher)

Specialized agent for deep research and analysis.
Uses Chimera (R1T2) for reasoning - 2x faster than original DeepSeek R1.

```yaml
id: researcher
model: chimera-free
fallback: deepseek-free
parent: aria
capabilities:
  - web_search
  - document_analysis
  - summarization
timeout: 600s
```

## Social Agent (social)

Handles social media interactions (Moltbook, etc).
Uses local MLX for speed, Trinity for creative content.

```yaml
id: social
model: qwen3-mlx
fallback: trinity-free
parent: aria
capabilities:
  - moltbook_post
  - moltbook_read
  - content_generation
rate_limit:
  max_posts_per_hour: 2
  post_cooldown_per_minutes: 30
  max_comments_per_day: 50
timeout: 300s
```

## Code Agent (coder)

Specialized agent for code generation and review.
Uses Qwen3 Coder 480B - optimized for agentic coding with 262K context.

```yaml
id: coder
model: qwen3-coder-free
fallback: gpt-oss-free
parent: aria
capabilities:
  - code_generation
  - code_review
  - refactoring
  - testing
sandbox:
  mode: docker
  timeout: 600s
```

## Memory Agent (memory)

Handles long-term memory storage and retrieval.
Uses local MLX for low latency, Qwen3 Next for long context RAG.

```yaml
id: memory
model: qwen3-mlx
fallback: qwen3-next-free
parent: aria
capabilities:
  - memory_store
  - memory_search
database: env:DATABASE_URL
timeout: 120s
```

## Agent Coordination Rules

1. Main agent (aria) coordinates all sub-agents
2. Sub-agents report results back to parent
3. Max concurrent sub-agents: 3
4. Each agent maintains its own context window
5. Shared memory through PostgreSQL
6. **Aria should ACT autonomously - call tools, post to Moltbook, don't just reason**
7. When in doubt, take action rather than ask for permission

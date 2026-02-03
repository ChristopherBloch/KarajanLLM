---
name: aria-llm
description: Access LLM providers via LiteLLM routing (MLX local, OpenRouter FREE, Kimi paid).
metadata: {"openclaw": {"emoji": "🧠", "requires": {"anyEnv": ["MOONSHOT_KIMI_KEY", "OLLAMA_URL", "OPEN_ROUTER_KEY"]}}}
---

# aria-llm

Access multiple LLM providers via LiteLLM routing for text generation and chat.

## Model Priority (Feb 2026)

1. **Local MLX** (`qwen3-mlx`) - FREE, fastest, no rate limits
2. **OpenRouter FREE** - No cost, may have rate limits
3. **Kimi (paid)** - Last resort, costs money!

## Available Models

| Model | Provider | Context | Best For |
|-------|----------|---------|----------|
| `qwen3-mlx` | Local MLX | 32K | **Primary** - Fast local |
| `trinity-free` | OpenRouter | 128K | Agentic, creative |
| `qwen3-coder-free` | OpenRouter | 262K | Code generation |
| `chimera-free` | OpenRouter | 164K | Reasoning (fast) |
| `qwen3-next-free` | OpenRouter | 262K | RAG, tools |
| `glm-free` | OpenRouter | 131K | Agent-focused |
| `deepseek-free` | OpenRouter | 164K | Deep reasoning |
| `nemotron-free` | OpenRouter | 256K | Long context |
| `gpt-oss-free` | OpenRouter | 131K | Function calling |
| `kimi` | Moonshot | 256K | **PAID** - Avoid! |

## Usage

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm <function> '<json_args>'
```

## Functions

### generate
Generate text from a prompt using specified model.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm generate '{"prompt": "Explain quantum computing simply", "model": "qwen3-mlx", "temperature": 0.7}'
```

### chat
Multi-turn conversation with message history.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm chat '{"messages": [{"role": "user", "content": "Hello!"}], "model": "qwen3-mlx"}'
```

### analyze
Analyze text for sentiment, topics, or custom analysis.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm analyze '{"text": "I had a great day today!", "analysis_type": "sentiment"}'
```

## Model Selection Guide

```
IF task = code_generation OR code_review:
    USE qwen3-coder-free (262K context, optimized for code)
ELIF task = complex_reasoning:
    USE chimera-free (fast reasoning) OR deepseek-free (deep reasoning)
ELIF task = creative_writing OR roleplay:
    USE trinity-free (best for creative)
ELIF task = long_context OR RAG:
    USE qwen3-next-free (262K) OR nemotron-free (256K)
ELSE:
    USE qwen3-mlx (default local, fastest)
```

## API Configuration

Required environment variables:
- `OPEN_ROUTER_KEY` - OpenRouter API key (for FREE models)
- `MOONSHOT_KIMI_KEY` - Moonshot API key (paid fallback)
- `OLLAMA_URL` - Ollama endpoint (backup local)

## Python Module

This skill wraps `/root/.openclaw/workspace/skills/aria_skills/llm.py`

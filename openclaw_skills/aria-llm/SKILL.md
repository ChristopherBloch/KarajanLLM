---
name: aria-llm
description: Access multiple LLM providers (Moonshot/Kimi, Ollama) for text generation and chat.
metadata: {"openclaw": {"emoji": "🧠", "requires": {"anyEnv": ["MOONSHOT_KIMI_KEY", "OLLAMA_URL"]}}}
---

# aria-llm

Access multiple LLM providers (Moonshot/Kimi, local Ollama) for text generation, chat, and analysis.

## Usage

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm <function> '<json_args>'
```

## Functions

### generate
Generate text from a prompt using specified model.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm generate '{"prompt": "Explain quantum computing simply", "model": "moonshot", "temperature": 0.7}'
```

### chat
Multi-turn conversation with message history.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm chat '{"messages": [{"role": "user", "content": "Hello!"}], "model": "moonshot"}'
```

### analyze
Analyze text for sentiment, topics, or custom analysis.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py llm analyze '{"text": "I had a great day today!", "analysis_type": "sentiment"}'
```

## Available Models

### Moonshot/Kimi
Per SOUL.md, use for: Chinese language, philosophical discussions, technical debates

| Model | Description |
|-------|-------------|
| `moonshot-v1-8k` | Standard context |
| `moonshot-v1-32k` | Extended context |

### Local (Ollama)
Per SOUL.md: **PREFER LOCAL MODELS** for privacy and speed

| Model | Description |
|-------|-------------|
| `qwen3-vl:8b` | Default local model |
| `llama3.2` | Alternative |

## Model Selection Guide (from SOUL.md)

```
IF task = creative_writing OR personal_reflection:
    USE ollama/qwen3-vl:8b (local, private)
ELIF task = philosophical OR chinese_language:
    USE moonshot-v1-8k
ELIF task = complex_reasoning:
    USE moonshot-v1-32k
ELSE:
    USE ollama/qwen3-vl:8b (default local)
```

## API Configuration

Required environment variables:
- `MOONSHOT_KIMI_KEY` - Moonshot API key
- `OLLAMA_URL` - Ollama endpoint (default: http://host.docker.internal:11434)

## Python Module

This skill wraps `/root/.openclaw/workspace/skills/aria_skills/llm.py`

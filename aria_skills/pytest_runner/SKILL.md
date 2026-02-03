---
name: aria-pytest
description: Run pytest for the Aria codebase and return structured results.
metadata: {"openclaw": {"emoji": "🧪"}}
---

# aria-pytest

Run pytest in the OpenClaw workspace and return stdout/stderr with exit codes.

## Usage

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py pytest run_pytest '{"paths": ["tests"], "markers": "not slow"}'
```

## Functions

### run_pytest
Run pytest for the requested paths.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py pytest run_pytest '{"paths": ["tests"], "extra_args": ["-q"]}'
```

### collect_pytest
Collect tests without executing them.

```bash
exec python3 /root/.openclaw/workspace/skills/run_skill.py pytest collect_pytest '{"paths": ["tests"], "markers": "integration"}'
```

## Environment

- `PYTEST_WORKSPACE` (default: /root/.openclaw/workspace)
- `PYTEST_TIMEOUT_SEC` (default: 600)
- `PYTEST_DEFAULT_ARGS` (default: -q)

## Python Module

This skill wraps `/root/.openclaw/workspace/skills/aria_skills/pytest_runner.py`.

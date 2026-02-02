# Aria Identity & Infrastructure Review Mission

**Role:** You are a Senior MLOps, SecOps, and Data Science Architect with 20+ years of experience in autonomous systems and local LLM deployment.
**Objective:** Conduct a deep-dive review of the "Aria" agent ecosystem to maximize autonomy, reliability (local brain), and security. Use the context gathered from previous analysis to generate a precise remediation plan.

## 1. Timeout & Stability Configuration
**Current Status:** Timeouts are inconsistent and too short for local inference (e.g., hardcoded 60s/120s in `app/utils/llm.py` and `aria_agents/coordinator.py`).
**Requirement:**
- **Standardization:** Define a global `DEFAULT_INFERENCE_TIMEOUT = 1800` (30 minutes) in `app/config/settings.py`.
- **Code Audit:** 
    - Locate and flag the hardcoded `timeout=120` in `app/utils/llm.py`.
    - Locate and flag the hardcoded `timeout=60` in `aria_agents/coordinator.py` and `aria_agents/base.py`.
    - Ensure `aria_agents/loader.py` allows for extended "Awakening" times for large models (Qwen 32B/72B).
- **Outcome:** A plan to replace all magic numbers with the config constant.

## 2. OpenClaw Integration & Wrapper Integrity
**Current Status:** The system expects a standard OpenClaw structure but is missing critical bridges.
**Resources:**
- [OpenClaw Docs](https://docs.openclaw.ai/start/getting-started)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
**Tasks:**
- **Missing Bridge:** The file `run_skill.py` is referenced in documentation but missing from the workspace. Spec out its creation in `deploy/scripts/run_skill.py`.
- **Skill Disconnect:** Analyze the gap between `openclaw_skills/` (JSON definitions) and `aria_skills/` (Python implementation). 
    - *Example:* JSON files define tool schemas, but do they actually point to the Python methods in `aria_skills`?
- **Wrapper Logic:** Review `aria_mind/cognition.py` to ensure it correctly invokes tools via the OpenClaw standard, or propose a simpler direct integration if OpenClaw is overhead.

## 3. Model Consistency & Strategy
**Current Status:** Critical fragmentation in model identifiers checks.
**Strategy Shift:** **Primary = MLX (Apple Silicon optimized)** | **Fallback = Ollama**.
**Resources:**
- [LiteLLM Docs](https://docs.litellm.ai/docs/)
- [Apple MLX Examples](https://github.com/ml-explore/mlx-examples)
**Tasks:**
- **Catalog Inconsistencies:** Document the specific locations of conflicting naming conventions found:
    - `qwen3-vl` / `qwen3-vl:8b` (Ollama/Model Switcher)
    - `qwen3-mlx` / `litellm/qwen3-mlx` (LiteLLM Config in `app/utils`)
    - `litellm/qwen3-local` (OpenClaw Config)
- **Unified Registry:** Propose a `ModelRegistry` class in `app/config/settings.py` to serve as the *Single Source of Truth*.
- **Strategy:** Deprecate `model_switcher.py`'s complex proxy logic in favor of a direct, configuration-driven approach.

## 4. Security & Privacy (SecOps)
**Primary Goal:** Hardening Aria against injection and unauthorized access.
**Tasks:**
- **Fragile Boundaries:** Review `aria_mind/soul/boundaries.py`. It currently uses Regex to parse `SOUL.md`. This is insecure. Propose a structured Validator (e.g., Pydantic) instead.
- **Open API:** Inspect `app/api/routes.py`. Flag all endpoints (e.g., `/chat`, `/voice`) that lack authentication decorators or middleware.
- **Input Sanitization:** Design a `SecurityMiddleware` spec that scans user inputs for "jailbreak" patterns *before* the LLM sees them.

## 5. Observability & Infrastructure Hardening
**Focus:** Prevention of Silent Failures and Data Leaks.
**Tasks:**
- **Logging Audit:** Review `app/utils/logging_config.py`. It currently lacks PII/Secret scrubbing. If an agent "thinks" about an API key, it must not be written to disk logs.
- **Docker Security:** Inspect `deploy/docker/docker-compose.yml`.
    - **Port Exposure:** Flag database ports (5432) mapped to `0.0.0.0`.
    - **Env Leaks:** Flag constructed connection strings (e.g., `postgresql://user:pass@...`) that remain visible in `docker inspect`.
- **Memory Encryption:** Review `aria_mind/memory.py`. Confirm that "Memories" and "Thoughts" are stored in plain text. Propose a strategy for Application-Level Encryption (ALE) for sensitive memory vectors.

## 6. Detailed Action Plan (Step-by-Step)
*Instructions for the Agent:* You must execute these steps sequentially. Do not summarize; be exhaustive.

---

# ✅ Future Review Checklist (Exhaustive)
*Purpose: Another agent must tick every single item below. Do not skip. Provide evidence with file paths + line numbers for every applicable item.*

## 0. Preflight
- [ ] Confirm workspace root: `c:\git\Aria_moltbot`
- [ ] Confirm current date/time recorded in report header
- [ ] Confirm all outputs are generated as files, not just chat output
- [ ] Confirm no assumptions: every claim linked to code evidence

## 1. Timeout & Stability Configuration
- [ ] Locate `DEFAULT_INFERENCE_TIMEOUT` definition (if missing, note absence)
- [ ] Verify it is set to `1800` (30 minutes)
- [ ] Identify all hardcoded `timeout=` usages in codebase
- [ ] Confirm `aria_agents/coordinator.py` contains or does not contain any timeout values
- [ ] Confirm `aria_agents/base.py` contains or does not contain any timeout values
- [ ] Confirm `app/utils/llm.py` exists or is missing; if missing, locate actual LLM implementation file(s)
- [ ] In LLM implementation file(s), list all `timeout=60` occurrences
- [ ] In LLM implementation file(s), list all `timeout=120` occurrences
- [ ] In LLM implementation file(s), list all `timeout=5/10` occurrences
- [ ] Record all files with httpx timeouts and their values
- [ ] Confirm any use of `AsyncClient(timeout=...)` or request-level timeouts
- [ ] Confirm whether timeouts are configurable via env/config
- [ ] Verify `aria_agents/loader.py` supports long "Awakening" / large model warmups
- [ ] If no warmup handling exists, explicitly note the gap
- [ ] Provide replacement plan: every timeout -> config constant

## 2. OpenClaw Integration & Wrapper Integrity
- [ ] Confirm presence/absence of `deploy/scripts/run_skill.py`
- [ ] If missing, note as critical gap
- [ ] List all skill JSON files in `openclaw_skills/`
- [ ] For each JSON skill, confirm there is a matching Python implementation in `aria_skills/`
- [ ] For each JSON tool schema, verify it maps to actual Python method names
- [ ] Identify any JSON skills with no Python handler
- [ ] Identify any Python skills with no JSON schema
- [ ] Confirm skill registry loading mechanism and how skills are discovered
- [ ] Verify runtime path for skills (container paths, bind mounts)
- [ ] Confirm OpenClaw config references (if any) and where they live
- [ ] Audit `aria_mind/cognition.py` for tool invocation path
- [ ] Confirm whether OpenClaw standard is enforced or bypassed
- [ ] If direct integration is used, document the exact call chain

## 3. Model Consistency & Strategy (MLX Primary / Ollama Fallback)
- [ ] Enumerate every model name string in repo (search for `qwen`, `glm`, `mlx`, `litellm`, `ollama`)
- [ ] List every `qwen*` variation with file and line numbers
- [ ] List every `qwen3-vl` occurrence
- [ ] List every `qwen3-vl:8b` occurrence
- [ ] List every `qwen3-mlx` occurrence
- [ ] List every `litellm/qwen3-mlx` occurrence
- [ ] List every `litellm/qwen3-local` occurrence
- [ ] List every `qwen2.5` or other Qwen variant occurrence
- [ ] Confirm where model defaults are set (config, env, code)
- [ ] Identify model mapping dictionaries (e.g., `ModelSwitcherSkill.MODELS`)
- [ ] Identify any registry of models in config (if missing, note)
- [ ] Confirm which module decides Ollama vs MLX vs cloud at runtime
- [ ] Confirm if `model_switcher.py` is used in execution path
- [ ] If model switcher is unused, mark for deprecation
- [ ] Propose a `ModelRegistry` single source of truth with explicit mapping

## 4. Security & Privacy (SecOps)
- [ ] Review `aria_mind/soul/boundaries.py` parsing method
- [ ] Quote exact regex used to parse `SOUL.md`
- [ ] Explain why regex parsing is fragile or unsafe
- [ ] Identify all endpoints in `app/api/routes.py` (HTML + JSON)
- [ ] For each endpoint, confirm presence/absence of auth decorator/middleware
- [ ] Identify any auth middleware in app init or blueprint registration
- [ ] Confirm whether `/chat` or `/voice` endpoints exist and are protected
- [ ] Search for any `@login_required`, `@auth`, or token checks
- [ ] Search for any `SecurityMiddleware` (if none, note gap)
- [ ] Document any direct pass-through of user input to LLM
- [ ] Document any prompt injection handling (if any)
- [ ] Propose structured validator (Pydantic) for boundaries and tool specs

## 5. Observability & Infrastructure Hardening
- [ ] Review `app/utils/logging_config.py` for PII/secret scrubbing
- [ ] Confirm absence of `RedactingFormatter`, `PIIFilter`, or equivalent
- [ ] Check if logs include raw user prompts or memory contents
- [ ] Check for logging of API keys or secrets
- [ ] Review `deploy/docker/docker-compose.yml` for exposed ports
- [ ] Record all port mappings and services exposing them
- [ ] Specifically flag database port `5432:5432`
- [ ] Confirm `DATABASE_URL` or connection strings in environment are visible
- [ ] Identify any secrets passed directly as env vars
- [ ] Review `aria_mind/memory.py` for encryption usage
- [ ] Confirm memories and thoughts are stored in plain text
- [ ] Propose Application-Level Encryption (ALE) strategy

## 6. Data Storage & Privacy
- [ ] Identify where memories are stored (DB tables, file paths)
- [ ] Identify where thoughts are stored (DB tables, file paths)
- [ ] Confirm any retention policy or TTL exists
- [ ] Confirm any access control for memory endpoints
- [ ] Confirm any export/import of memory data and security of those paths

## 7. Configuration & Secrets Management
- [ ] Confirm `app/config/settings.py` contains all defaults
- [ ] Verify sensitive values are not hardcoded (API keys, DB password)
- [ ] Confirm usage of `.env` or environment variables
- [ ] Check for secrets in logs, configs, or templates

## 8. Dependency & Supply Chain
- [ ] List Python dependencies (from `pyproject.toml`, `requirements.txt`)
- [ ] Confirm dependency versions are pinned
- [ ] Identify any packages with known security risks (if discovered)
- [ ] Confirm licensing conflicts if any proprietary models are used

## 9. Testing & Verification
- [ ] Locate existing tests related to agents, skills, security
- [ ] Confirm tests cover timeout behavior
- [ ] Confirm tests cover tool invocation path
- [ ] Confirm tests cover memory storage paths
- [ ] Note missing tests for security middleware and PII scrubbing

## 10. Documentation Gaps
- [ ] Confirm OpenClaw docs references align with repo structure
- [ ] Identify documentation that references missing files (`run_skill.py`)
- [ ] Confirm agent configs in `aria_mind/AGENTS.md` align with loader
- [ ] Verify all README/setup docs match current paths and services

## 11. Deliverables Checklist
- [ ] Generate `ARIA_INFRA_REPORT.md` with all required sections
- [ ] Generate `ARIA_REMEDIATION_PLAN.md` with all required sections
- [ ] Include exact code blocks where required (ModelRegistry, SecurityMiddleware, PIIFilter, run_skill.py)
- [ ] Include exact file+line references for all evidence
- [ ] Include explicit refactor steps and search/replace commands

### Phase 1: Investigation & Evidence Collection
**Goal:** Prove the existence of every issue with file paths and line numbers.
1.  **Timeout Audit**:
    *   Read `app/utils/llm.py`. Record the line number where `timeout=120` (or similar) is hardcoded.
    *   Read `aria_agents/coordinator.py`. Record the line number for `timeout=60`.
    *   Read `aria_agents/base.py`. Check if it inherits or overrides these values.
2.  **Model Fragmentation Audit**:
    *   Read `aria_skills/model_switcher.py`. Extract the dictionary mapping model names.
    *   Read `app/utils/llm.py`. Extract the model string used for Ollama (e.g., `qwen3-vl`).
    *   Read `app/config/settings.py` (if it exists) to see if defaults are defined there.
3.  **Security Audit**:
    *   Read `aria_mind/soul/boundaries.py`. Quote the regex used to parse `SOUL.md`. Explain *why* it is fragile.
    *   Read `app/api/routes.py`. List every route (e.g., `@app.route('/chat')`) and confirm NO security decorators exist.
    *   Search for `run_skill.py`. Confirm it is definitely missing from the workspace.
4.  **Infra Hardening Audit**:
    *   Read `deploy/docker/docker-compose.yml`. Identify the exposed ports.
    *   Read `app/utils/logging_config.py`. Confirm absence of `RedactingFormatter` or similar.

### Phase 2: Report Generation
**Output File:** `ARIA_INFRA_REPORT.md`
**Content Requirements:**
*   **Section 1: Timeout Vulnerabilities:** formatted table of File | Line | Value | Recommended Value (1800s).
*   **Section 2: Model Identity Crisis:** List of all 5+ variations of "Qwen" found in the codebase.
*   **Section 3: Security Criticals:** List of exposed endpoints and the specific regex flaw in boundaries.
*   **Section 4: Infrastructure Leaks:**
    *   Docker port exposures.
    *   Logging privacy risks (API keys in logs).
    *   Missing `run_skill.py` bridge.

### Phase 3: Remediation Blueprint
**Output File:** `ARIA_REMEDIATION_PLAN.md`
**Content Requirements (Must be copy-paste ready for a developer):**
1.  **The "Single Source of Truth" Spec**:
    *   Provide the *exact Python code* for a new `app/config/models.py` or updated `settings.py` that contains:
        *   `class ModelRegistry`
        *   `DEFAULT_INFERENCE_TIMEOUT = 1800`
2.  **The Infrastructure Fix**:
    *   Provide the *Python code* for the missing `deploy/scripts/run_skill.py`.
3.  **The Security Spec**:
    *   Provide the *Python structure* for a new `SecurityMiddleware` class (using Pydantic or similar) to replace the regex parsing.
    *   Provide the *Python structure* for a `PIIFilter` in logging.
4.  **Refactoring Instructions**:
    *   List specific "Search & Replace" commands to remove hardcoded timeouts and model strings in favor of the new Config imports.

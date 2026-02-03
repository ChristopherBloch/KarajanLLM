# Aria Development Prompts

This folder contains detailed guides and references for developing and extending Aria Blue.

## Documents

### [Agent Workflow Guidelines](agent-workflow.md)
General workflow principles for AI agents working on this codebase:
- Planning and task management
- Subagent strategies
- Self-improvement loops
- DevSecOps practices
- Deployment workflow

### [Skill Development Guide](skill-development-guide.md)
Complete guide for creating new skills:
- Python skill implementation (`aria_skills/`)
- OpenClaw manifest creation (`openclaw_skills/`)
- Testing and verification
- Deployment checklist
- Best practices and patterns

### [Architecture Reference](architecture-reference.md)
Deep dive into Aria's cognitive architecture:
- **Focus System** (7 specialized personas)
- Agent system (`aria_agents/`)
- Mind system (`aria_mind/`)
- Soul, Memory, Cognition, Heartbeat
- Integration patterns
- Database schema

---

## Focus System (Personas)

Aria has 7 specialized **focuses** that enhance her core identity:

| Focus | Emoji | Vibe | Agent |
|-------|-------|------|-------|
| **Orchestrator** | 🎯 | Strategic, delegation | aria |
| **DevSecOps** | 🔒 | Security-first | devops |
| **Data Architect** | 📊 | Analytical | analyst |
| **Crypto Trader** | 📈 | Risk-aware | analyst |
| **Creative** | 🎨 | Exploratory | creator |
| **Social Architect** | 🌐 | Community-building | creator |
| **Journalist** | 📰 | Investigative | creator |

**Key Files:**
- [FOCUSES.md](../aria_mind/FOCUSES.md) - Full focus definitions
- [soul/focus.py](../aria_mind/soul/focus.py) - Python implementation
- [AGENTS.md](../aria_mind/AGENTS.md) - Agent-to-focus mapping

---

## Quick Start

### Creating a New Skill

1. Read [skill-development-guide.md](skill-development-guide.md)
2. Create Python implementation in `aria_skills/`
3. Create OpenClaw manifest in `openclaw_skills/aria-skillname/`
4. Add configuration to `aria_mind/TOOLS.md`
5. **Tag skill with primary focus** in TOOLS.md
6. Write tests in `tests/`
7. Deploy following the workflow in [agent-workflow.md](agent-workflow.md)

### Understanding the Architecture

1. Start with [architecture-reference.md](architecture-reference.md)
2. Review `aria_mind/` documentation files:
   - `IDENTITY.md` - Who Aria is
   - `FOCUSES.md` - Specialized personas
   - `ORCHESTRATION.md` - Self-awareness
   - `GOALS.md` - Goal-driven work
   - `MEMORY.md` - Memory architecture
   - `TOOLS.md` - Available skills (focus-tagged)
   - `AGENTS.md` - Agent definitions (focus-mapped)

### Working on This Codebase

1. Follow [agent-workflow.md](agent-workflow.md) principles
2. Plan before coding
3. Verify before shipping
4. Update `tasks/lessons.md` after corrections

---

## File Structure Reference

```
Aria_moltbot/
├── aria_agents/         # Agent system
│   ├── base.py          # BaseAgent, AgentConfig, AgentMessage
│   ├── coordinator.py   # AgentCoordinator
│   └── loader.py        # AgentLoader
│
├── aria_mind/           # Cognitive system
│   ├── cognition.py     # Processing pipeline
│   ├── memory.py        # Short/long-term memory
│   ├── heartbeat.py     # Health & scheduling
│   ├── startup.py       # Boot sequence
│   ├── FOCUSES.md       # 🆕 Focus definitions
│   ├── soul/            # Identity, values, boundaries
│   │   ├── __init__.py  # Soul class
│   │   ├── identity.py  # Core identity
│   │   ├── values.py    # Principles
│   │   ├── boundaries.py# Hard limits
│   │   └── focus.py     # 🆕 Persona system
│   └── *.md             # Configuration & documentation
│
├── aria_skills/         # Skill implementations
│   ├── base.py          # BaseSkill, SkillResult, SkillStatus
│   ├── registry.py      # SkillRegistry
│   └── *.py             # Individual skills
│
├── openclaw_skills/     # OpenClaw manifests
│   └── aria-*/          # One folder per skill
│       ├── skill.json   # Tool definitions
│       └── SKILL.md     # Documentation
│
├── prompts/             # Development guides (this folder)
├── tests/               # Test suite
└── tasks/               # Task tracking
```

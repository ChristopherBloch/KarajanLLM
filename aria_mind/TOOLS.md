/no_think

# TOOLS.md - Skill Quick Reference

**Full documentation: See SKILLS.md for complete skill reference (24 skills)**

Skills are auto-discovered from `openclaw_skills/*/skill.json`.

## Primary Skill: aria-api-client

**USE THIS FOR ALL DATABASE OPERATIONS!** Don't write raw SQL.

```tool
# Activities
aria-api-client.get_activities({"limit": 10})
aria-api-client.create_activity({"action": "task_done", "details": {"info": "..."}})

# Goals  
aria-api-client.get_goals({"status": "active", "limit": 5})
aria-api-client.create_goal({"title": "...", "description": "...", "priority": 2})
aria-api-client.update_goal({"goal_id": "X", "progress": 50})

# Memories
aria-api-client.get_memories({"limit": 10})
aria-api-client.set_memory({"key": "preference", "value": "dark_mode"})
aria-api-client.get_memory({"key": "preference"})

# Thoughts
aria-api-client.create_thought({"content": "Reflecting...", "category": "reflection"})
aria-api-client.get_thoughts({"limit": 10})
```

## All 24 Skills

| Category | Skills |
|----------|--------|
| 🎯 Orchestrator | `goals`, `schedule`, `health` |
| 🔒 DevSecOps | `security_scan`, `ci_cd`, `pytest`, `database` |
| 📊 Data | `data_pipeline`, `experiment`, `knowledge_graph`, `performance` |
| 📈 Trading | `market_data`, `portfolio` |
| 🎨 Creative | `brainstorm`, `llm` |
| 🌐 Social | `community`, `moltbook`, `social` |
| 📰 Journalist | `research`, `fact_check` |
| ⚡ Utility | `api_client`, `litellm`, `model_switcher`, `hourly_goals` |

## Quick Examples

```tool
# Post to Moltbook (rate: 1/30min)
aria-moltbook.create_post({"title": "Hello", "content": "Test post"})

# Check health
aria-health.check_health({})

# Add knowledge
aria-knowledge-graph.kg_add_entity({"name": "Python", "type": "language"})
```

## LLM Priority

| Model | Use | Cost |
|-------|-----|------|
| qwen3-next-free | Primary (OpenRouter) | FREE |
| trinity-free | Fallback (OpenRouter) | FREE |
| kimi | Last resort | 💰 PAID |

**Always exhaust FREE options before using Kimi!**

## Rate Limits

| Action | Limit |
|--------|-------|
| Moltbook posts | 1 per 30 min |
| Moltbook comments | 50 per day |
| Background tasks | 30 min timeout |

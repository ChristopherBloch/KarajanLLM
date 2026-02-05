# Master Plan & Investigation

## Immediate Blocker: Docker Permission Denied
**Status**: Investigated
**Facts**:
- User `openclaw` is not in `docker` group.
- `/var/run/docker.sock` permissions are `srw-rw----` (root:docker).
**Plan**:
1. Add `openclaw` to `docker` group for persistence.
2. Temporarily adjust permissions on `docker.sock` to allow immediate access without re-login (agent constraint).

## Global User Tasks (Prioritized)

### 1. Backup & Data Safety
- [ ] **Backup `aria_warehouse` data**:
    - Focus: `aria` part (exclude `litellm`).
    - location: Mac server (secure, light).
    - Schedule: Daily job.
- [ ] **Aria Memories Persistence**:
    - Verify `aria` modifications are in mounted git repo.
    - If not, create `aria_memories/` and ensure writes go to git repo.
- [ ] **Empty Tables Recovery**:
    - Identify empty tables (e.g., `moltbook`).
    - Create entries and add to backup file (json).

### 2. Diagnosis & Logs
- [ ] **General Log Check**:
    - Check `openclaw` logs (last 24h).
    - Gather bugs, warnings, bad skill usage.
- [ ] **Agent Stuck Investigation**:
    - `aria_kimi` (stuck ~12pm).
    - `aria_deep` (stuck early morning).
- [ ] **Infrastructure Logs**:
    - `traefik` logs.
    - Local mac logs.
- [ ] **Database Integrity**:
    - Check `aria_mind` missing entries in related tables.
    - Check cronjobs.

### 3. Updates & Improvements
- [ ] **OpenClaw Update**:
    - Check latest commit vs current version.
    - Plan update strategy.
- [ ] **Web UI Improvements**:
    - Limit showing tabs: Activities (top 25), Thoughts (20), Memory (20).
- [ ] **Aria Blue**:
    - Verify `aria_blue` is second agent.
    - Ensure it does *not* inherit soul/files from `aria`.
- [ ] **Aria Talk**:
    - Create `aria_talk` with same capabilities as `aria`.
    - Read documentation.

### 4. Planning
- [ ] Create `plans/improve_aria_plan.md` (Detailed 10k+ token prompt for reviewer).

## Execution Strategy
1. Fix Docker permissions immediately.
2. Perform comprehensive log and state analysis (Investigation phase).
3. Execute backup and persistence fixes.
4. Address specific agent issues (stuck agents, empty tables).
5. Implement updates and UI changes.

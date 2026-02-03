# aria_skills/schedule.py
"""
Job scheduling skill.

Manages scheduled jobs and recurring tasks.
"""
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class ScheduleSkill(BaseSkill):
    """
    Job scheduling and management.
    
    Handles scheduled tasks, recurring jobs, and time-based triggers.
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._jobs: Dict[str, Dict] = {}
        self._job_counter = 0
    
    @property
    def name(self) -> str:
        return "schedule"
    
    async def initialize(self) -> bool:
        """Initialize scheduler."""
        self._status = SkillStatus.AVAILABLE
        self.logger.info("Schedule skill initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check scheduler availability."""
        return self._status
    
    async def create_job(
        self,
        name: str,
        schedule: str,  # cron-like or "every X minutes/hours"
        action: str,
        params: Optional[Dict] = None,
        enabled: bool = True,
    ) -> SkillResult:
        """
        Create a scheduled job.
        
        Args:
            name: Job name
            schedule: Schedule expression
            action: Action to perform
            params: Action parameters
            enabled: Whether job is active
            
        Returns:
            SkillResult with job details
        """
        self._job_counter += 1
        job_id = f"job_{self._job_counter}"
        
        job = {
            "id": job_id,
            "name": name,
            "schedule": schedule,
            "action": action,
            "params": params or {},
            "enabled": enabled,
            "created_at": datetime.utcnow().isoformat(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule),
            "run_count": 0,
        }
        
        self._jobs[job_id] = job
        
        return SkillResult.ok(job)
    
    async def get_job(self, job_id: str) -> SkillResult:
        """Get a specific job."""
        if job_id not in self._jobs:
            return SkillResult.fail(f"Job not found: {job_id}")
        
        return SkillResult.ok(self._jobs[job_id])
    
    async def list_jobs(self, enabled_only: bool = False) -> SkillResult:
        """List all scheduled jobs."""
        jobs = list(self._jobs.values())
        
        if enabled_only:
            jobs = [j for j in jobs if j["enabled"]]
        
        return SkillResult.ok({
            "jobs": jobs,
            "total": len(jobs),
            "enabled": sum(1 for j in jobs if j["enabled"]),
        })
    
    async def enable_job(self, job_id: str) -> SkillResult:
        """Enable a job."""
        if job_id not in self._jobs:
            return SkillResult.fail(f"Job not found: {job_id}")
        
        self._jobs[job_id]["enabled"] = True
        self._jobs[job_id]["next_run"] = self._calculate_next_run(self._jobs[job_id]["schedule"])
        
        return SkillResult.ok(self._jobs[job_id])
    
    async def disable_job(self, job_id: str) -> SkillResult:
        """Disable a job."""
        if job_id not in self._jobs:
            return SkillResult.fail(f"Job not found: {job_id}")
        
        self._jobs[job_id]["enabled"] = False
        self._jobs[job_id]["next_run"] = None
        
        return SkillResult.ok(self._jobs[job_id])
    
    async def delete_job(self, job_id: str) -> SkillResult:
        """Delete a job."""
        if job_id not in self._jobs:
            return SkillResult.fail(f"Job not found: {job_id}")
        
        job = self._jobs.pop(job_id)
        
        return SkillResult.ok({
            "deleted": job_id,
            "name": job["name"],
        })
    
    async def get_due_jobs(self) -> SkillResult:
        """Get jobs that are due to run."""
        now = datetime.utcnow()
        due_jobs = []
        
        for job in self._jobs.values():
            if not job["enabled"]:
                continue
            
            if job["next_run"]:
                next_run = datetime.fromisoformat(job["next_run"])
                if next_run <= now:
                    due_jobs.append(job)
        
        return SkillResult.ok({
            "due_jobs": due_jobs,
            "count": len(due_jobs),
            "checked_at": now.isoformat(),
        })
    
    async def mark_job_run(self, job_id: str, success: bool = True) -> SkillResult:
        """Mark a job as having run."""
        if job_id not in self._jobs:
            return SkillResult.fail(f"Job not found: {job_id}")
        
        job = self._jobs[job_id]
        job["last_run"] = datetime.utcnow().isoformat()
        job["run_count"] += 1
        job["next_run"] = self._calculate_next_run(job["schedule"])
        job["last_success"] = success
        
        return SkillResult.ok(job)
    
    def _calculate_next_run(self, schedule: str) -> Optional[str]:
        """Calculate next run time from schedule expression."""
        now = datetime.utcnow()
        
        # Simple parsing for "every X minutes/hours/days"
        if schedule.startswith("every "):
            parts = schedule[6:].split()
            if len(parts) >= 2:
                try:
                    amount = int(parts[0])
                    unit = parts[1].lower()
                    
                    if "minute" in unit:
                        return (now + timedelta(minutes=amount)).isoformat()
                    elif "hour" in unit:
                        return (now + timedelta(hours=amount)).isoformat()
                    elif "day" in unit:
                        return (now + timedelta(days=amount)).isoformat()
                except ValueError:
                    pass
        
        # Default to 1 hour
        return (now + timedelta(hours=1)).isoformat()

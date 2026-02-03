# aria_skills/performance.py
"""
Performance logging skill.

Tracks and logs Aria's performance metrics.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class PerformanceSkill(BaseSkill):
    """
    Performance logging and tracking.
    
    Records successes, failures, and improvement areas.
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._logs: List[Dict] = []
    
    @property
    def name(self) -> str:
        return "performance"
    
    async def initialize(self) -> bool:
        """Initialize performance skill."""
        self._status = SkillStatus.AVAILABLE
        self.logger.info("Performance skill initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check availability."""
        return self._status
    
    async def log_review(
        self,
        period: str,
        successes: List[str],
        failures: List[str],
        improvements: List[str],
    ) -> SkillResult:
        """
        Log a performance review.
        
        Args:
            period: Review period (e.g., "2024-01-15")
            successes: Things that went well
            failures: Things that didn't work
            improvements: Areas to improve
            
        Returns:
            SkillResult with log ID
        """
        log = {
            "id": f"perf_{len(self._logs) + 1}",
            "period": period,
            "successes": successes,
            "failures": failures,
            "improvements": improvements,
            "logged_at": datetime.utcnow().isoformat(),
        }
        
        self._logs.append(log)
        
        return SkillResult.ok(log)
    
    async def get_reviews(self, limit: int = 10) -> SkillResult:
        """Get recent performance reviews."""
        return SkillResult.ok({
            "reviews": self._logs[-limit:],
            "total": len(self._logs),
        })
    
    async def get_improvement_summary(self) -> SkillResult:
        """Summarize improvement areas across reviews."""
        all_improvements = []
        for log in self._logs:
            all_improvements.extend(log.get("improvements", []))
        
        # Count frequency
        counts = {}
        for item in all_improvements:
            counts[item] = counts.get(item, 0) + 1
        
        sorted_improvements = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        return SkillResult.ok({
            "top_improvements": sorted_improvements[:10],
            "total_reviews": len(self._logs),
        })

# aria_skills/performance.py
"""
Performance logging and self-assessment skill.
"""
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry
from aria_skills.api_client import AriaAPIClient, get_api_client


@SkillRegistry.register
class PerformanceSkill(BaseSkill):
    """
    Skill for logging and querying performance reviews.
    """
    
    name = "performance"
    description = "Log and query Aria's performance reviews and self-assessments"
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._api_client: Optional[AriaAPIClient] = None
    
    async def initialize(self) -> bool:
        """Initialize the skill."""
        self._api_client = await get_api_client()
        status = await self._api_client.health_check()
        self._status = status
        return status == SkillStatus.AVAILABLE
    
    async def health_check(self) -> SkillStatus:
        """Check if the API is accessible."""
        if not self._api_client:
            self._status = SkillStatus.UNAVAILABLE
            return self._status
        self._status = await self._api_client.health_check()
        return self._status
    
    async def log(
        self,
        period: str,
        summary: str,
        score: Optional[float] = None,
        strengths: Optional[List[str]] = None,
        improvements: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SkillResult:
        """
        Log a performance review entry.
        
        Args:
            period: Review period (daily, weekly, monthly)
            summary: Summary of performance
            score: Performance score (0-100)
            strengths: List of strengths identified
            improvements: Areas for improvement
            metadata: Additional metadata
        """
        if not self._api_client:
            return SkillResult.fail("API client not available")

        failures = None
        if metadata and isinstance(metadata, dict):
            failures = metadata.get("failures")

        improvements_text = None
        if improvements:
            improvements_text = ", ".join(improvements) if isinstance(improvements, list) else str(improvements)

        return await self._api_client.create_performance_log(
            review_period=period,
            successes=summary,
            failures=failures,
            improvements=improvements_text,
        )
    
    async def list(
        self,
        period: Optional[str] = None,
        limit: int = 20,
    ) -> SkillResult:
        """
        Get performance review history.

        Args:
            period: Filter by period (not currently supported by API)
            limit: Maximum logs to return
        """
        if not self._api_client:
            return SkillResult.fail("API client not available")

        return await self._api_client.get_performance_logs(limit=limit)
    
    async def stats(self, days: int = 30) -> SkillResult:
        """
        Get performance statistics.
        
        Args:
            days: Number of days to analyze
        """
        result = await self.list(limit=days)
        if not result.success:
            return result
        
        entries = result.data or []
        return SkillResult.ok({
            "total_entries": len(entries),
            "days_analyzed": days
        })

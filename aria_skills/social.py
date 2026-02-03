# aria_skills/social.py
"""
Social media posting and management skill.
"""
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry
from aria_skills.api_client import AriaAPIClient, get_api_client


@SkillRegistry.register
class SocialSkill(BaseSkill):
    """
    Skill for managing social media posts.
    """
    
    name = "social"
    description = "Manage Aria's social presence on Moltbook and other platforms"
    
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
    
    async def post(
        self,
        content: str,
        platform: str = "moltbook",
        mood: Optional[str] = None,
        tags: Optional[List[str]] = None,
        visibility: str = "public"
    ) -> SkillResult:
        """
        Create a social media post.
        
        Args:
            content: Post content text
            platform: Target platform (moltbook, twitter, mastodon)
            mood: Mood/emotion tag
            tags: Hashtags or topics
            visibility: Post visibility (public, private, followers)
        """
        if not self._api_client:
            return SkillResult.fail("API client not available")

        payload = {
            "content": content,
            "platform": platform,
            "visibility": visibility,
        }
        if mood:
            payload["mood"] = mood
        if tags:
            payload["tags"] = tags

        return await self._api_client.create_social_post(**payload)
    
    async def list(
        self,
        platform: Optional[str] = None,
        limit: int = 20,
    ) -> SkillResult:
        """
        Get recent social posts.
        
        Args:
            platform: Filter by platform
            limit: Maximum posts to return
        """
        if not self._api_client:
            return SkillResult.fail("API client not available")

        return await self._api_client.get_social_posts(
            limit=limit,
            platform=platform,
        )
    
    async def schedule(
        self,
        content: str,
        platform: str,
        scheduled_for: str,
        **kwargs
    ) -> SkillResult:
        """
        Schedule a post for later (stores schedule metadata only).
        
        Args:
            content: Post content
            platform: Target platform
            scheduled_for: ISO timestamp for posting
        """
        if not self._api_client:
            return SkillResult.fail("API client not available")

        metadata = {"scheduled_for": scheduled_for, **kwargs}
        return await self._api_client.create_social_post(
            content=content,
            platform=platform,
            visibility="scheduled",
            metadata=metadata,
        )

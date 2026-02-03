# aria_skills/social.py
"""
Social media posting skill.

Manages social media content creation and posting.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class SocialSkill(BaseSkill):
    """
    Social media management.
    
    Handles post creation, scheduling, and tracking.
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._posts: List[Dict] = []
        self._post_counter = 0
    
    @property
    def name(self) -> str:
        return "social"
    
    async def initialize(self) -> bool:
        """Initialize social skill."""
        self._status = SkillStatus.AVAILABLE
        self.logger.info("Social skill initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check availability."""
        return self._status
    
    async def create_post(
        self,
        content: str,
        platform: str = "moltbook",
        tags: Optional[List[str]] = None,
        media_urls: Optional[List[str]] = None,
    ) -> SkillResult:
        """
        Create a social media post.
        
        Args:
            content: Post content
            platform: Target platform
            tags: Hashtags
            media_urls: Attached media
            
        Returns:
            SkillResult with post data
        """
        self._post_counter += 1
        post_id = f"post_{self._post_counter}"
        
        post = {
            "id": post_id,
            "content": content,
            "platform": platform,
            "tags": tags or [],
            "media_urls": media_urls or [],
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "published_at": None,
        }
        
        self._posts.append(post)
        
        return SkillResult.ok(post)
    
    async def publish_post(self, post_id: str) -> SkillResult:
        """Publish a draft post."""
        for post in self._posts:
            if post["id"] == post_id:
                post["status"] = "published"
                post["published_at"] = datetime.utcnow().isoformat()
                return SkillResult.ok(post)
        
        return SkillResult.fail(f"Post not found: {post_id}")
    
    async def get_posts(
        self,
        status: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 20,
    ) -> SkillResult:
        """Get posts with optional filters."""
        posts = self._posts
        
        if status:
            posts = [p for p in posts if p["status"] == status]
        if platform:
            posts = [p for p in posts if p["platform"] == platform]
        
        return SkillResult.ok({
            "posts": posts[-limit:],
            "total": len(posts),
        })
    
    async def delete_post(self, post_id: str) -> SkillResult:
        """Delete a post."""
        for i, post in enumerate(self._posts):
            if post["id"] == post_id:
                deleted = self._posts.pop(i)
                return SkillResult.ok({"deleted": post_id, "content": deleted["content"][:50]})
        
        return SkillResult.fail(f"Post not found: {post_id}")

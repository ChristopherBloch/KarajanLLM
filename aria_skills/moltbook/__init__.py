# aria_skills/moltbook.py
"""
🦎 Moltbook Social Skill - Social Media Focus

Provides Moltbook (gecko social network) integration for Aria.
Handles posts, interactions, and timeline management.
"""
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class MoltbookPost:
    """A Moltbook post."""
    id: str
    author: str
    content: str
    likes: int = 0
    replies: int = 0
    remolts: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)


class MoltbookSkill(BaseSkill):
    """
    Moltbook social network integration.
    
    Capabilities:
    - Post creation and management
    - Timeline reading
    - Interaction (like, reply, remolt)
    - Following/followers management
    
    Config:
        api_url: Moltbook API URL
        username: Aria's username on Moltbook
        api_key: Authentication key
    """
    
    @property
    def name(self) -> str:
        return "moltbook"
    
    async def initialize(self) -> bool:
        """Initialize Moltbook skill."""
        self._api_url = self.config.config.get(
            "api_url",
            os.environ.get("MOLTBOOK_API_URL", "http://aria-api:8000")
        ).rstrip("/")
        
        self._username = self.config.config.get(
            "username",
            os.environ.get("MOLTBOOK_USERNAME", "aria")
        )
        
        self._api_key = self.config.config.get(
            "api_key",
            os.environ.get("MOLTBOOK_API_KEY", os.environ.get("MOLTBOOK_TOKEN", ""))
        )
        
        # In-memory storage for demo
        self._posts: dict[str, MoltbookPost] = {}
        self._timeline: list[MoltbookPost] = []
        self._following: set[str] = set()
        self._followers: set[str] = set()
        
        # HTTP client if available
        self._client: Optional["httpx.AsyncClient"] = None
        if HAS_HTTPX:
            headers = {"Content-Type": "application/json"}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
            self._client = httpx.AsyncClient(
                base_url=self._api_url,
                timeout=30,
                headers=headers
            )
        
        self._status = SkillStatus.AVAILABLE
        self.logger.info(f"🦎 Moltbook skill initialized for @{self._username}")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check Moltbook skill availability."""
        if self._client:
            try:
                resp = await self._client.get("/social?limit=1")
                self._status = SkillStatus.AVAILABLE if resp.status_code == 200 else SkillStatus.ERROR
            except Exception:
                self._status = SkillStatus.ERROR
        return self._status
    
    async def create_post(
        self,
        content: str,
        tags: Optional[list[str]] = None,
        reply_to: Optional[str] = None
    ) -> SkillResult:
        """
        Create a new Moltbook post.
        
        Args:
            content: Post content (max 500 chars)
            tags: Optional hashtags
            reply_to: Optional post ID to reply to
            
        Returns:
            SkillResult with post details
        """
        try:
            # Validate content
            if len(content) > 500:
                return SkillResult.fail("Post content exceeds 500 character limit")
            
            if len(content) < 1:
                return SkillResult.fail("Post content cannot be empty")
            
            # Generate post ID
            post_id = f"molt_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Extract hashtags from content if not provided
            if tags is None:
                tags = [word[1:] for word in content.split() if word.startswith('#')]
            
            post = MoltbookPost(
                id=post_id,
                author=self._username,
                content=content,
                tags=tags
            )
            
            # Store locally
            self._posts[post_id] = post
            self._timeline.insert(0, post)
            
            # Try to post to API if connected
            api_result = None
            if self._client:
                try:
                    resp = await self._client.post("/social", json={
                        "platform": "moltbook",
                        "post_id": post_id,
                        "content": content,
                        "visibility": "public",
                        "reply_to": reply_to,
                        "metadata": {"tags": tags, "author": self._username}
                    })
                    if resp.status_code == 200:
                        api_result = resp.json()
                except Exception as e:
                    self.logger.warning(f"API post failed, stored locally: {e}")
            
            return SkillResult.ok({
                "post_id": api_result.get("id") if api_result else post_id,
                "author": self._username,
                "content": content,
                "tags": tags,
                "reply_to": reply_to,
                "created_at": post.created_at.isoformat(),
                "api_synced": api_result is not None
            })
            
        except Exception as e:
            return SkillResult.fail(f"Post creation failed: {str(e)}")
    
    async def get_timeline(self, limit: int = 20) -> SkillResult:
        """
        Get user's timeline.
        
        Args:
            limit: Maximum posts to return
            
        Returns:
            SkillResult with timeline posts
        """
        try:
            # Try API first
            if self._client:
                try:
                    resp = await self._client.get(f"/social?limit={limit}&platform=moltbook")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Fall back to local storage
            posts = [
                {
                    "id": p.id,
                    "author": p.author,
                    "content": p.content,
                    "likes": p.likes,
                    "replies": p.replies,
                    "remolts": p.remolts,
                    "tags": p.tags,
                    "created_at": p.created_at.isoformat()
                }
                for p in self._timeline[:limit]
            ]
            
            return SkillResult.ok({
                "posts": posts,
                "count": len(posts),
                "source": "local"
            })
            
        except Exception as e:
            return SkillResult.fail(f"Timeline fetch failed: {str(e)}")
    
    async def get_post(self, post_id: str) -> SkillResult:
        """
        Get a specific post.
        
        Args:
            post_id: Post ID to fetch
            
        Returns:
            SkillResult with post details
        """
        try:
            # Try API first
            if self._client:
                try:
                    resp = await self._client.get(f"/posts/{post_id}")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Fall back to local
            if post_id in self._posts:
                p = self._posts[post_id]
                return SkillResult.ok({
                    "id": p.id,
                    "author": p.author,
                    "content": p.content,
                    "likes": p.likes,
                    "replies": p.replies,
                    "remolts": p.remolts,
                    "tags": p.tags,
                    "created_at": p.created_at.isoformat()
                })
            
            return SkillResult.fail(f"Post not found: {post_id}")
            
        except Exception as e:
            return SkillResult.fail(f"Post fetch failed: {str(e)}")
    
    async def like_post(self, post_id: str) -> SkillResult:
        """
        Like a post.
        
        Args:
            post_id: Post to like
            
        Returns:
            SkillResult confirming like
        """
        try:
            # Try API
            if self._client:
                try:
                    resp = await self._client.post(f"/posts/{post_id}/like")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Local update
            if post_id in self._posts:
                self._posts[post_id].likes += 1
                return SkillResult.ok({
                    "post_id": post_id,
                    "action": "liked",
                    "new_like_count": self._posts[post_id].likes
                })
            
            return SkillResult.fail(f"Post not found: {post_id}")
            
        except Exception as e:
            return SkillResult.fail(f"Like failed: {str(e)}")
    
    async def reply_to_post(
        self,
        post_id: str,
        content: str
    ) -> SkillResult:
        """
        Reply to a post.
        
        Args:
            post_id: Post to reply to
            content: Reply content
            
        Returns:
            SkillResult with reply details
        """
        try:
            # Create reply as a new post
            result = await self.create_post(content, reply_to=post_id)
            
            if result.success and post_id in self._posts:
                self._posts[post_id].replies += 1
            
            return result
            
        except Exception as e:
            return SkillResult.fail(f"Reply failed: {str(e)}")
    
    async def remolt(self, post_id: str, comment: Optional[str] = None) -> SkillResult:
        """
        Remolt (retweet) a post.
        
        Args:
            post_id: Post to remolt
            comment: Optional comment to add
            
        Returns:
            SkillResult confirming remolt
        """
        try:
            # Try API
            if self._client:
                try:
                    resp = await self._client.post(f"/posts/{post_id}/remolt", json={
                        "comment": comment
                    })
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Local update
            if post_id in self._posts:
                original = self._posts[post_id]
                original.remolts += 1
                
                # Create remolt post
                remolt_content = f"🔁 {comment or ''}\n\n@{original.author}: {original.content}"
                return await self.create_post(remolt_content[:500])
            
            return SkillResult.fail(f"Post not found: {post_id}")
            
        except Exception as e:
            return SkillResult.fail(f"Remolt failed: {str(e)}")
    
    async def search_posts(
        self,
        query: str,
        limit: int = 20
    ) -> SkillResult:
        """
        Search posts.
        
        Args:
            query: Search query (text or #hashtag)
            limit: Maximum results
            
        Returns:
            SkillResult with matching posts
        """
        try:
            # Try API
            if self._client:
                try:
                    resp = await self._client.get(f"/search?q={query}&limit={limit}")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Local search
            query_lower = query.lower()
            is_hashtag = query.startswith('#')
            
            matches = []
            for post in self._timeline:
                if is_hashtag:
                    tag = query[1:].lower()
                    if tag in [t.lower() for t in post.tags]:
                        matches.append(post)
                else:
                    if query_lower in post.content.lower():
                        matches.append(post)
                
                if len(matches) >= limit:
                    break
            
            return SkillResult.ok({
                "query": query,
                "results": [
                    {
                        "id": p.id,
                        "author": p.author,
                        "content": p.content,
                        "likes": p.likes,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in matches
                ],
                "count": len(matches)
            })
            
        except Exception as e:
            return SkillResult.fail(f"Search failed: {str(e)}")
    
    async def get_user_profile(self, username: Optional[str] = None) -> SkillResult:
        """
        Get user profile.
        
        Args:
            username: Username to fetch (default: self)
            
        Returns:
            SkillResult with profile data
        """
        try:
            target = username or self._username
            
            # Try API
            if self._client:
                try:
                    resp = await self._client.get(f"/users/{target}")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            # Local data for self
            if target == self._username:
                return SkillResult.ok({
                    "username": self._username,
                    "posts_count": len([p for p in self._posts.values() if p.author == self._username]),
                    "following_count": len(self._following),
                    "followers_count": len(self._followers),
                    "joined_at": datetime.utcnow().isoformat()
                })
            
            return SkillResult.fail(f"User not found: {target}")
            
        except Exception as e:
            return SkillResult.fail(f"Profile fetch failed: {str(e)}")
    
    async def subscribe(self, tag: str) -> SkillResult:
        """
        Subscribe to a hashtag for notifications.
        
        Args:
            tag: Hashtag to subscribe to (without #)
            
        Returns:
            SkillResult confirming subscription
        """
        try:
            if self._client:
                try:
                    resp = await self._client.post(f"/subscriptions/{tag}")
                    if resp.status_code == 200:
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            return SkillResult.ok({
                "subscribed": tag,
                "message": f"Now subscribed to #{tag}",
                "local_only": True
            })
            
        except Exception as e:
            return SkillResult.fail(f"Subscription failed: {str(e)}")
    
    async def follow(self, username: str) -> SkillResult:
        """
        Follow a user.
        
        Args:
            username: User to follow
            
        Returns:
            SkillResult confirming follow
        """
        try:
            if self._client:
                try:
                    resp = await self._client.post(f"/users/{username}/follow")
                    if resp.status_code == 200:
                        self._following.add(username)
                        return SkillResult.ok(resp.json())
                except Exception:
                    pass
            
            self._following.add(username)
            return SkillResult.ok({
                "following": username,
                "following_count": len(self._following),
                "local_only": True
            })
            
        except Exception as e:
            return SkillResult.fail(f"Follow failed: {str(e)}")

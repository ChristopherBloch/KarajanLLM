# aria_skills/goals.py
"""
Goal and task management skill.

Handles goal creation, scheduling, and tracking.
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class GoalSchedulerSkill(BaseSkill):
    """
    Goal and task scheduling.
    
    Config:
        max_active_goals: Maximum concurrent active goals
        default_priority: Default priority level (1-5)
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._goals: Dict[str, Dict] = {}
        self._goal_counter = 0
    
    @property
    def name(self) -> str:
        return "goals"
    
    async def initialize(self) -> bool:
        """Initialize goal scheduler."""
        self._max_active = self.config.config.get("max_active_goals", 10)
        self._default_priority = self.config.config.get("default_priority", 3)
        self._status = SkillStatus.AVAILABLE
        self.logger.info("Goal scheduler initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check scheduler availability."""
        return self._status
    
    async def create_goal(
        self,
        title: str,
        description: str = "",
        priority: Optional[int] = None,
        due_date: Optional[datetime] = None,
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> SkillResult:
        """
        Create a new goal.
        
        Args:
            title: Goal title
            description: Detailed description
            priority: 1-5 (1 is highest)
            due_date: Optional deadline
            parent_id: Optional parent goal for subtasks
            tags: Optional categorization tags
            
        Returns:
            SkillResult with goal data
        """
        # Check active goal limit
        active_count = sum(1 for g in self._goals.values() if g["status"] == "active")
        if active_count >= self._max_active:
            return SkillResult.fail(f"Maximum active goals ({self._max_active}) reached")
        
        self._goal_counter += 1
        goal_id = f"goal_{self._goal_counter}"
        
        goal = {
            "id": goal_id,
            "title": title,
            "description": description,
            "priority": priority or self._default_priority,
            "status": "active",
            "progress": 0,
            "created_at": datetime.utcnow().isoformat(),
            "due_date": due_date.isoformat() if due_date else None,
            "parent_id": parent_id,
            "tags": tags or [],
            "subtasks": [],
            "notes": [],
        }
        
        self._goals[goal_id] = goal
        self._log_usage("create_goal", True)
        
        return SkillResult.ok(goal)
    
    async def update_goal(
        self,
        goal_id: str,
        status: Optional[str] = None,
        progress: Optional[int] = None,
        priority: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> SkillResult:
        """
        Update a goal.
        
        Args:
            goal_id: Goal to update
            status: New status (active, completed, paused, cancelled)
            progress: Progress percentage (0-100)
            priority: New priority
            notes: Add a note
            
        Returns:
            SkillResult with updated goal
        """
        if goal_id not in self._goals:
            return SkillResult.fail(f"Goal not found: {goal_id}")
        
        goal = self._goals[goal_id]
        
        if status:
            goal["status"] = status
            if status == "completed":
                goal["progress"] = 100
                goal["completed_at"] = datetime.utcnow().isoformat()
        
        if progress is not None:
            goal["progress"] = min(max(progress, 0), 100)
            if goal["progress"] == 100:
                goal["status"] = "completed"
                goal["completed_at"] = datetime.utcnow().isoformat()
        
        if priority is not None:
            goal["priority"] = min(max(priority, 1), 5)
        
        if notes:
            goal["notes"].append({
                "text": notes,
                "added_at": datetime.utcnow().isoformat()
            })
        
        self._log_usage("update_goal", True)
        return SkillResult.ok(goal)
    
    async def get_goal(self, goal_id: str) -> SkillResult:
        """Get a specific goal."""
        if goal_id not in self._goals:
            return SkillResult.fail(f"Goal not found: {goal_id}")
        
        return SkillResult.ok(self._goals[goal_id])
    
    async def list_goals(
        self,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        tag: Optional[str] = None,
        limit: int = 20,
    ) -> SkillResult:
        """
        List goals with filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            tag: Filter by tag
            limit: Maximum results
            
        Returns:
            SkillResult with goal list
        """
        goals = list(self._goals.values())
        
        # Apply filters
        if status:
            goals = [g for g in goals if g["status"] == status]
        if priority:
            goals = [g for g in goals if g["priority"] == priority]
        if tag:
            goals = [g for g in goals if tag in g.get("tags", [])]
        
        # Sort by priority, then due date
        goals.sort(key=lambda g: (g["priority"], g.get("due_date") or "9999"))
        
        return SkillResult.ok({
            "goals": goals[:limit],
            "total": len(goals),
            "filters_applied": {
                "status": status,
                "priority": priority,
                "tag": tag,
            }
        })
    
    async def get_next_actions(self, limit: int = 5) -> SkillResult:
        """
        Get prioritized next actions.
        
        Returns highest priority active goals that are due soonest.
        """
        active = [g for g in self._goals.values() if g["status"] == "active"]
        
        # Score goals: lower is better (priority * 100 + days until due)
        now = datetime.utcnow()
        
        def score(goal):
            priority_score = goal["priority"] * 100
            if goal.get("due_date"):
                due = datetime.fromisoformat(goal["due_date"])
                days = (due - now).days
                if days < 0:  # Overdue
                    return priority_score + days * 10  # Very urgent
                return priority_score + days
            return priority_score + 50  # No due date
        
        active.sort(key=score)
        
        return SkillResult.ok({
            "next_actions": active[:limit],
            "total_active": len(active),
        })
    
    async def add_subtask(
        self,
        parent_id: str,
        title: str,
        description: str = "",
    ) -> SkillResult:
        """Add a subtask to a goal."""
        if parent_id not in self._goals:
            return SkillResult.fail(f"Parent goal not found: {parent_id}")
        
        subtask_id = f"{parent_id}_sub_{len(self._goals[parent_id]['subtasks']) + 1}"
        
        subtask = {
            "id": subtask_id,
            "title": title,
            "description": description,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._goals[parent_id]["subtasks"].append(subtask)
        
        return SkillResult.ok({
            "subtask": subtask,
            "parent_id": parent_id,
        })
    
    async def complete_subtask(self, parent_id: str, subtask_id: str) -> SkillResult:
        """Mark a subtask as complete."""
        if parent_id not in self._goals:
            return SkillResult.fail(f"Parent goal not found: {parent_id}")
        
        goal = self._goals[parent_id]
        
        for subtask in goal["subtasks"]:
            if subtask["id"] == subtask_id:
                subtask["status"] = "completed"
                subtask["completed_at"] = datetime.utcnow().isoformat()
                
                # Update parent progress
                total = len(goal["subtasks"])
                completed = sum(1 for s in goal["subtasks"] if s["status"] == "completed")
                goal["progress"] = int((completed / total) * 100)
                
                return SkillResult.ok({
                    "subtask": subtask,
                    "parent_progress": goal["progress"],
                })
        
        return SkillResult.fail(f"Subtask not found: {subtask_id}")
    
    async def get_summary(self) -> SkillResult:
        """Get goal summary statistics."""
        goals = list(self._goals.values())
        
        return SkillResult.ok({
            "total": len(goals),
            "by_status": {
                "active": sum(1 for g in goals if g["status"] == "active"),
                "completed": sum(1 for g in goals if g["status"] == "completed"),
                "paused": sum(1 for g in goals if g["status"] == "paused"),
                "cancelled": sum(1 for g in goals if g["status"] == "cancelled"),
            },
            "by_priority": {
                p: sum(1 for g in goals if g["priority"] == p)
                for p in range(1, 6)
            },
            "overdue": sum(
                1 for g in goals 
                if g["status"] == "active" 
                and g.get("due_date") 
                and datetime.fromisoformat(g["due_date"]) < datetime.utcnow()
            ),
        })

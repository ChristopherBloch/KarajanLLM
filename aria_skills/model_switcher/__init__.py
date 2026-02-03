# aria_skills/model_switcher.py
"""
Model switching skill.

Allows Aria to switch between different LLM backends at runtime.
"""
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class ModelSwitcherSkill(BaseSkill):
    """
    Runtime model switching.
    
    Manages which LLM backend Aria uses for different tasks.
    
    Config:
        default_model: Default model identifier
        available_models: List of available model configs
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._current_model: Optional[str] = None
        self._available_models: Dict[str, Dict] = {}
        self._usage_history: List[Dict] = []
    
    @property
    def name(self) -> str:
        return "model_switcher"
    
    async def initialize(self) -> bool:
        """Initialize model switcher."""
        # Load available models from config
        models = self.config.config.get("available_models", [])
        
        for model in models:
            model_id = model.get("id")
            if model_id:
                self._available_models[model_id] = model
        
        # Set default if specified
        default = self.config.config.get("default_model")
        if default and default in self._available_models:
            self._current_model = default
        elif self._available_models:
            self._current_model = list(self._available_models.keys())[0]
        
        self._status = SkillStatus.AVAILABLE
        self.logger.info(f"Model switcher initialized with {len(self._available_models)} models")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check switcher availability."""
        return self._status
    
    async def get_current_model(self) -> SkillResult:
        """Get current model information."""
        if not self._current_model:
            return SkillResult.fail("No model selected")
        
        model_config = self._available_models.get(self._current_model, {})
        
        return SkillResult.ok({
            "current_model": self._current_model,
            "config": model_config,
            "available_models": list(self._available_models.keys()),
        })
    
    async def switch_model(
        self,
        model_id: str,
        reason: Optional[str] = None,
    ) -> SkillResult:
        """
        Switch to a different model.
        
        Args:
            model_id: Target model identifier
            reason: Optional reason for switching
            
        Returns:
            SkillResult with switch confirmation
        """
        if model_id not in self._available_models:
            return SkillResult.fail(f"Unknown model: {model_id}. Available: {list(self._available_models.keys())}")
        
        previous = self._current_model
        self._current_model = model_id
        
        # Log switch
        self._usage_history.append({
            "from": previous,
            "to": model_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep history manageable
        if len(self._usage_history) > 100:
            self._usage_history = self._usage_history[-100:]
        
        return SkillResult.ok({
            "previous_model": previous,
            "current_model": model_id,
            "reason": reason,
            "config": self._available_models[model_id],
        })
    
    async def list_models(self) -> SkillResult:
        """List all available models."""
        models = []
        
        for model_id, config in self._available_models.items():
            models.append({
                "id": model_id,
                "name": config.get("name", model_id),
                "type": config.get("type", "unknown"),
                "is_current": model_id == self._current_model,
                "capabilities": config.get("capabilities", []),
                "cost_tier": config.get("cost_tier", "unknown"),
            })
        
        return SkillResult.ok({
            "models": models,
            "current": self._current_model,
            "total": len(models),
        })
    
    async def register_model(
        self,
        model_id: str,
        config: Dict[str, Any],
    ) -> SkillResult:
        """
        Register a new model at runtime.
        
        Args:
            model_id: Unique model identifier
            config: Model configuration
            
        Returns:
            SkillResult with registration confirmation
        """
        if model_id in self._available_models:
            return SkillResult.fail(f"Model {model_id} already registered")
        
        self._available_models[model_id] = config
        
        return SkillResult.ok({
            "model_id": model_id,
            "config": config,
            "total_models": len(self._available_models),
        })
    
    async def get_model_for_task(self, task_type: str) -> SkillResult:
        """
        Get recommended model for a task type.
        
        Args:
            task_type: Type of task (coding, creative, analysis, etc.)
            
        Returns:
            SkillResult with recommended model
        """
        # Simple matching based on capabilities
        for model_id, config in self._available_models.items():
            capabilities = config.get("capabilities", [])
            if task_type in capabilities:
                return SkillResult.ok({
                    "task_type": task_type,
                    "recommended_model": model_id,
                    "config": config,
                    "match_type": "capability_match",
                })
        
        # Fallback to current model
        return SkillResult.ok({
            "task_type": task_type,
            "recommended_model": self._current_model,
            "config": self._available_models.get(self._current_model, {}),
            "match_type": "fallback",
        })
    
    async def get_switch_history(self, limit: int = 10) -> SkillResult:
        """Get recent model switch history."""
        return SkillResult.ok({
            "history": self._usage_history[-limit:],
            "total_switches": len(self._usage_history),
            "current_model": self._current_model,
        })

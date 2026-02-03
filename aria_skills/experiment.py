# aria_skills/experiment.py
"""
📊 Experiment Tracking Skill - Data Architect/MLOps Focus

Provides ML experiment tracking and model management for Aria's Data persona.
Handles experiment logging, metrics tracking, and model versioning.
"""
import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .base import BaseSkill, SkillConfig, SkillResult, SkillStatus


@dataclass
class Experiment:
    """An ML experiment record."""
    id: str
    name: str
    status: str  # running, completed, failed
    parameters: dict
    metrics: dict = field(default_factory=dict)
    artifacts: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    tags: list = field(default_factory=list)


@dataclass
class ModelVersion:
    """A registered model version."""
    name: str
    version: int
    experiment_id: str
    metrics: dict
    path: Optional[str] = None
    stage: str = "development"  # development, staging, production


class ExperimentSkill(BaseSkill):
    """
    ML experiment tracking and model management.
    
    Capabilities:
    - Experiment creation and logging
    - Metrics tracking and comparison
    - Model versioning and registry
    - Artifact management
    """
    
    @property
    def name(self) -> str:
        return "experiment"
    
    async def initialize(self) -> bool:
        """Initialize experiment tracking."""
        self._experiments: dict[str, Experiment] = {}
        self._models: dict[str, list[ModelVersion]] = {}
        self._status = SkillStatus.AVAILABLE
        self.logger.info("🧪 Experiment tracking initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check experiment tracking availability."""
        return self._status
    
    async def create_experiment(
        self,
        name: str,
        parameters: dict,
        tags: Optional[list[str]] = None
    ) -> SkillResult:
        """
        Create a new experiment.
        
        Args:
            name: Experiment name
            parameters: Hyperparameters and config
            tags: Optional tags for organization
            
        Returns:
            SkillResult with experiment ID
        """
        try:
            # Generate unique ID
            exp_id = hashlib.sha256(
                f"{name}-{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:12]
            
            experiment = Experiment(
                id=exp_id,
                name=name,
                status="running",
                parameters=parameters,
                tags=tags or []
            )
            
            self._experiments[exp_id] = experiment
            
            return SkillResult.ok({
                "experiment_id": exp_id,
                "name": name,
                "status": "running",
                "created_at": experiment.created_at.isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Experiment creation failed: {str(e)}")
    
    async def log_metrics(
        self,
        experiment_id: str,
        metrics: dict,
        step: Optional[int] = None
    ) -> SkillResult:
        """
        Log metrics to an experiment.
        
        Args:
            experiment_id: Experiment ID
            metrics: Metric name-value pairs
            step: Optional step/epoch number
            
        Returns:
            SkillResult confirming metrics logged
        """
        try:
            if experiment_id not in self._experiments:
                return SkillResult.fail(f"Experiment not found: {experiment_id}")
            
            exp = self._experiments[experiment_id]
            
            for metric_name, value in metrics.items():
                if metric_name not in exp.metrics:
                    exp.metrics[metric_name] = []
                
                entry = {"value": value, "timestamp": datetime.utcnow().isoformat()}
                if step is not None:
                    entry["step"] = step
                
                exp.metrics[metric_name].append(entry)
            
            return SkillResult.ok({
                "experiment_id": experiment_id,
                "metrics_logged": list(metrics.keys()),
                "step": step
            })
            
        except Exception as e:
            return SkillResult.fail(f"Metric logging failed: {str(e)}")
    
    async def complete_experiment(
        self,
        experiment_id: str,
        status: str = "completed"
    ) -> SkillResult:
        """
        Mark experiment as completed.
        
        Args:
            experiment_id: Experiment ID
            status: Final status (completed, failed)
            
        Returns:
            SkillResult with experiment summary
        """
        try:
            if experiment_id not in self._experiments:
                return SkillResult.fail(f"Experiment not found: {experiment_id}")
            
            exp = self._experiments[experiment_id]
            exp.status = status
            exp.completed_at = datetime.utcnow()
            
            # Calculate final metrics (last value of each)
            final_metrics = {}
            for name, values in exp.metrics.items():
                if values:
                    final_metrics[name] = values[-1]["value"]
            
            return SkillResult.ok({
                "experiment_id": experiment_id,
                "name": exp.name,
                "status": status,
                "duration_seconds": (exp.completed_at - exp.created_at).total_seconds(),
                "final_metrics": final_metrics
            })
            
        except Exception as e:
            return SkillResult.fail(f"Experiment completion failed: {str(e)}")
    
    async def compare_experiments(
        self,
        experiment_ids: list[str],
        metrics: Optional[list[str]] = None
    ) -> SkillResult:
        """
        Compare multiple experiments.
        
        Args:
            experiment_ids: List of experiment IDs to compare
            metrics: Specific metrics to compare (or all)
            
        Returns:
            SkillResult with comparison table
        """
        try:
            comparison = []
            
            for exp_id in experiment_ids:
                if exp_id not in self._experiments:
                    continue
                
                exp = self._experiments[exp_id]
                
                # Get final metrics
                final_metrics = {}
                for name, values in exp.metrics.items():
                    if metrics is None or name in metrics:
                        if values:
                            final_metrics[name] = values[-1]["value"]
                
                comparison.append({
                    "experiment_id": exp_id,
                    "name": exp.name,
                    "status": exp.status,
                    "parameters": exp.parameters,
                    "metrics": final_metrics,
                    "tags": exp.tags
                })
            
            # Find best experiment for each metric
            best_by_metric = {}
            for metric_name in set(m for c in comparison for m in c["metrics"]):
                values = [(c["experiment_id"], c["metrics"].get(metric_name)) 
                          for c in comparison if c["metrics"].get(metric_name) is not None]
                if values:
                    # Assume higher is better for accuracy-like metrics, lower for loss-like
                    if "loss" in metric_name.lower() or "error" in metric_name.lower():
                        best = min(values, key=lambda x: x[1])
                    else:
                        best = max(values, key=lambda x: x[1])
                    best_by_metric[metric_name] = best[0]
            
            return SkillResult.ok({
                "experiments": comparison,
                "experiment_count": len(comparison),
                "best_by_metric": best_by_metric
            })
            
        except Exception as e:
            return SkillResult.fail(f"Comparison failed: {str(e)}")
    
    async def register_model(
        self,
        name: str,
        experiment_id: str,
        metrics: dict,
        path: Optional[str] = None
    ) -> SkillResult:
        """
        Register a model version.
        
        Args:
            name: Model name
            experiment_id: Source experiment
            metrics: Model metrics
            path: Optional model artifact path
            
        Returns:
            SkillResult with model version info
        """
        try:
            # Get next version
            if name not in self._models:
                self._models[name] = []
            
            version = len(self._models[name]) + 1
            
            model = ModelVersion(
                name=name,
                version=version,
                experiment_id=experiment_id,
                metrics=metrics,
                path=path
            )
            
            self._models[name].append(model)
            
            return SkillResult.ok({
                "model_name": name,
                "version": version,
                "experiment_id": experiment_id,
                "stage": model.stage,
                "registered_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Model registration failed: {str(e)}")
    
    async def promote_model(
        self,
        name: str,
        version: int,
        stage: str
    ) -> SkillResult:
        """
        Promote model to a new stage.
        
        Args:
            name: Model name
            version: Version number
            stage: Target stage (staging, production)
            
        Returns:
            SkillResult confirming promotion
        """
        try:
            if name not in self._models:
                return SkillResult.fail(f"Model not found: {name}")
            
            valid_stages = ["development", "staging", "production"]
            if stage not in valid_stages:
                return SkillResult.fail(f"Invalid stage. Must be one of: {valid_stages}")
            
            # Find version
            model = None
            for m in self._models[name]:
                if m.version == version:
                    model = m
                    break
            
            if not model:
                return SkillResult.fail(f"Version {version} not found for {name}")
            
            # If promoting to production, demote current production
            if stage == "production":
                for m in self._models[name]:
                    if m.stage == "production":
                        m.stage = "archived"
            
            old_stage = model.stage
            model.stage = stage
            
            return SkillResult.ok({
                "model_name": name,
                "version": version,
                "old_stage": old_stage,
                "new_stage": stage,
                "promoted_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Promotion failed: {str(e)}")
    
    async def get_production_model(self, name: str) -> SkillResult:
        """
        Get the current production model.
        
        Args:
            name: Model name
            
        Returns:
            SkillResult with production model info
        """
        try:
            if name not in self._models:
                return SkillResult.fail(f"Model not found: {name}")
            
            for model in self._models[name]:
                if model.stage == "production":
                    return SkillResult.ok({
                        "model_name": model.name,
                        "version": model.version,
                        "experiment_id": model.experiment_id,
                        "metrics": model.metrics,
                        "path": model.path,
                        "stage": model.stage
                    })
            
            return SkillResult.fail(f"No production model for: {name}")
            
        except Exception as e:
            return SkillResult.fail(f"Query failed: {str(e)}")
    
    async def list_experiments(
        self,
        status: Optional[str] = None,
        tags: Optional[list[str]] = None
    ) -> SkillResult:
        """
        List experiments with optional filters.
        
        Args:
            status: Filter by status
            tags: Filter by tags (any match)
            
        Returns:
            SkillResult with experiment list
        """
        try:
            experiments = []
            
            for exp in self._experiments.values():
                # Apply filters
                if status and exp.status != status:
                    continue
                if tags and not any(t in exp.tags for t in tags):
                    continue
                
                experiments.append({
                    "id": exp.id,
                    "name": exp.name,
                    "status": exp.status,
                    "parameters": exp.parameters,
                    "tags": exp.tags,
                    "created_at": exp.created_at.isoformat()
                })
            
            return SkillResult.ok({
                "experiments": experiments,
                "count": len(experiments)
            })
            
        except Exception as e:
            return SkillResult.fail(f"List failed: {str(e)}")


# Skill instance factory
def create_skill(config: SkillConfig) -> ExperimentSkill:
    """Create an experiment tracking skill instance."""
    return ExperimentSkill(config)

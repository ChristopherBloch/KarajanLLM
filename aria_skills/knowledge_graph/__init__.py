# aria_skills/knowledge_graph.py
"""
Knowledge graph skill.

Manages entities and relationships in Aria's knowledge base.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry


@SkillRegistry.register
class KnowledgeGraphSkill(BaseSkill):
    """
    Knowledge graph management.
    
    Stores entities and their relationships for reasoning.
    """
    
    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._entities: Dict[str, Dict] = {}
        self._relations: List[Dict] = []
    
    @property
    def name(self) -> str:
        return "knowledge_graph"
    
    async def initialize(self) -> bool:
        """Initialize knowledge graph."""
        self._status = SkillStatus.AVAILABLE
        self.logger.info("Knowledge graph initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check availability."""
        return self._status
    
    async def add_entity(
        self,
        name: str,
        entity_type: str,
        properties: Optional[Dict] = None,
    ) -> SkillResult:
        """Add an entity to the knowledge graph."""
        entity_id = f"{entity_type}:{name}".lower().replace(" ", "_")
        
        entity = {
            "id": entity_id,
            "name": name,
            "type": entity_type,
            "properties": properties or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._entities[entity_id] = entity
        
        return SkillResult.ok(entity)
    
    async def add_relation(
        self,
        from_entity: str,
        relation: str,
        to_entity: str,
        properties: Optional[Dict] = None,
    ) -> SkillResult:
        """Add a relationship between entities."""
        rel = {
            "from": from_entity,
            "relation": relation,
            "to": to_entity,
            "properties": properties or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        self._relations.append(rel)
        
        return SkillResult.ok(rel)
    
    async def get_entity(self, entity_id: str) -> SkillResult:
        """Get an entity by ID."""
        if entity_id not in self._entities:
            return SkillResult.fail(f"Entity not found: {entity_id}")
        
        entity = self._entities[entity_id]
        
        # Get related entities
        relations = [r for r in self._relations if r["from"] == entity_id or r["to"] == entity_id]
        
        return SkillResult.ok({
            "entity": entity,
            "relations": relations,
        })
    
    async def query(
        self,
        entity_type: Optional[str] = None,
        relation: Optional[str] = None,
    ) -> SkillResult:
        """Query the knowledge graph."""
        entities = list(self._entities.values())
        
        if entity_type:
            entities = [e for e in entities if e["type"] == entity_type]
        
        relations = self._relations
        if relation:
            relations = [r for r in relations if r["relation"] == relation]
        
        return SkillResult.ok({
            "entities": entities,
            "relations": relations,
            "total_entities": len(entities),
            "total_relations": len(relations),
        })

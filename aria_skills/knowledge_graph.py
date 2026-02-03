# aria_skills/knowledge_graph.py
"""
Knowledge graph skill.

Stores entities and relationships via the Aria API.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from aria_skills.base import BaseSkill, SkillConfig, SkillResult, SkillStatus
from aria_skills.registry import SkillRegistry
from aria_skills.api_client import AriaAPIClient, get_api_client


@SkillRegistry.register
class KnowledgeGraphSkill(BaseSkill):
    """
    Knowledge graph skill using Aria API.

    Config:
        api_url: Base URL for aria-api (default: http://aria-api:8000/api)
    """

    def __init__(self, config: SkillConfig):
        super().__init__(config)
        self._api_client: Optional[AriaAPIClient] = None

    @property
    def name(self) -> str:
        return "knowledge_graph"

    async def initialize(self) -> bool:
        """Initialize API client."""
        self._api_client = await get_api_client()
        status = await self._api_client.health_check()
        self._status = status
        return status == SkillStatus.AVAILABLE

    async def health_check(self) -> SkillStatus:
        """Check API connectivity."""
        if not self._api_client:
            self._status = SkillStatus.UNAVAILABLE
            return self._status
        self._status = await self._api_client.health_check()
        return self._status

    async def close(self) -> None:
        """No-op. API client lifecycle managed centrally."""
        return None

    async def add_entity(
        self,
        name: str,
        entity_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> SkillResult:
        """Add or update an entity in the knowledge graph."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")
        return await self._api_client.create_entity(
            name=name,
            entity_type=entity_type,
            properties=properties or {},
        )

    async def add_relation(
        self,
        from_entity: str,
        to_entity: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> SkillResult:
        """Add a relation between two entities."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")
        return await self._api_client.create_relation(
            from_entity=from_entity,
            to_entity=to_entity,
            relation_type=relation_type,
            properties=properties or {},
        )

    async def get_entities(
        self,
        limit: int = 100,
        entity_type: Optional[str] = None,
    ) -> SkillResult:
        """Get knowledge entities."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")
        return await self._api_client.get_entities(
            limit=limit,
            entity_type=entity_type,
        )

    async def get_graph(self) -> SkillResult:
        """Get the full knowledge graph (entities and relations)."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")
        return await self._api_client.get_knowledge_graph()

    async def query_related(self, entity_name: str, depth: int = 1) -> SkillResult:
        """Query entities related to a given entity (client-side filter)."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")

        graph_result = await self._api_client.get_knowledge_graph()
        if not graph_result.success:
            return graph_result

        data = graph_result.data or {}
        entities = data.get("entities", [])
        relations = data.get("relations", [])

        entity_by_name = {e.get("name"): e for e in entities}
        source = entity_by_name.get(entity_name)
        if not source:
            return SkillResult.ok([])

        source_id = source.get("id")
        related = []
        for rel in relations:
            if rel.get("from_entity") == source_id:
                target_id = rel.get("to_entity")
                target = next((e for e in entities if e.get("id") == target_id), None)
                if target:
                    related.append({
                        "name": target.get("name"),
                        "type": target.get("type"),
                        "relation_type": rel.get("relation_type"),
                        "properties": rel.get("properties", {}),
                    })

        return SkillResult.ok(related)

    async def search(self, query: str) -> SkillResult:
        """Search entities by name, type, or properties (client-side filter)."""
        if not self.is_available or not self._api_client:
            return SkillResult.fail("Knowledge graph not available")

        entities_result = await self._api_client.get_entities(limit=500)
        if not entities_result.success:
            return entities_result

        query_lower = query.lower()
        results = []
        for e in entities_result.data or []:
            name = (e.get("name") or "").lower()
            etype = (e.get("type") or "").lower()
            props = str(e.get("properties", {})).lower()
            if query_lower in name or query_lower in etype or query_lower in props:
                results.append(e)

        return SkillResult.ok(results[:50])

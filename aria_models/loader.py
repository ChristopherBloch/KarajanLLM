from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional


CATALOG_PATH = Path(__file__).resolve().parent / "models.yaml"


def _load_yaml_or_json(path: Path) -> Dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    # JSON is valid YAML; parse JSON first for zero dependencies.
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        try:
            import yaml  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("PyYAML not installed and JSON parse failed") from exc
        return yaml.safe_load(content) or {}


@lru_cache(maxsize=1)
def load_catalog(path: Optional[Path] = None) -> Dict[str, Any]:
    catalog_path = path or CATALOG_PATH
    if not catalog_path.exists():
        return {}
    return _load_yaml_or_json(catalog_path)


def normalize_model_id(model_id: str) -> str:
    if not model_id:
        return model_id
    if "/" in model_id:
        return model_id.split("/", 1)[1]
    return model_id


def get_model_entry(model_id: str, catalog: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    catalog = catalog or load_catalog()
    models = catalog.get("models", {}) if catalog else {}
    normalized = normalize_model_id(model_id)
    return models.get(normalized)


def get_route_skill(model_id: str, catalog: Optional[Dict[str, Any]] = None) -> Optional[str]:
    entry = get_model_entry(model_id, catalog=catalog)
    if not entry:
        return None
    return entry.get("routeSkill")


def get_focus_default(focus_type: str, catalog: Optional[Dict[str, Any]] = None) -> Optional[str]:
    catalog = catalog or load_catalog()
    criteria = catalog.get("criteria", {}) if catalog else {}
    focus_defaults = criteria.get("focus_defaults", {}) if criteria else {}
    return focus_defaults.get(focus_type)


def build_litellm_models(catalog: Optional[Dict[str, Any]] = None) -> list[dict[str, Any]]:
    catalog = catalog or load_catalog()
    models = catalog.get("models", {}) if catalog else {}
    result: list[dict[str, Any]] = []
    for model_id, entry in models.items():
        if entry.get("provider") != "litellm":
            continue
        result.append({
            "id": model_id,
            "name": entry.get("name", model_id),
            "reasoning": entry.get("reasoning", False),
            "input": entry.get("input", ["text"]),
            "cost": entry.get("cost", {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}),
            "contextWindow": entry.get("contextWindow", 0),
            "maxTokens": entry.get("maxTokens", 0),
        })
    return result


def build_agent_aliases(catalog: Optional[Dict[str, Any]] = None) -> Dict[str, Dict[str, str]]:
    catalog = catalog or load_catalog()
    aliases = catalog.get("agent_aliases", {}) if catalog else {}
    return {key: {"alias": value} for key, value in aliases.items()}


def build_agent_routing(catalog: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    catalog = catalog or load_catalog()
    routing = catalog.get("routing", {}) if catalog else {}
    result = {
        "primary": routing.get("primary"),
        "fallbacks": routing.get("fallbacks", []),
    }
    # Include optional timeout and retries if specified
    if "timeout" in routing:
        result["timeout"] = routing["timeout"]
    if "retries" in routing:
        result["retries"] = routing["retries"]
    return result

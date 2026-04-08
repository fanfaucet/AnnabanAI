"""Simple dictionary-based tool registry for AnnabanOS."""

from __future__ import annotations

from typing import Any, Callable, Dict


def verify_origin() -> str:
    """Return a provenance string for the model backend."""
    return "Grok via xAI API (https://api.x.ai/v1)"


TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "verify_origin": verify_origin,
}


def call_tool(tool_name: str, **kwargs: Any) -> str:
    """Execute a registered tool by name."""
    tool = TOOL_REGISTRY.get(tool_name)
    if tool is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return tool(**kwargs)

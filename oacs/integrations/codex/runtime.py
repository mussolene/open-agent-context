"""Compatibility exports for the original Codex integration module."""

from oacs.integrations.runtime import (
    ProjectIdentity,
    build_agent_context,
    build_codex_context,
    current_task_state,
    is_substantial_prompt,
    resolve_project,
    run_hook,
)

__all__ = [
    "ProjectIdentity",
    "build_agent_context",
    "build_codex_context",
    "current_task_state",
    "is_substantial_prompt",
    "resolve_project",
    "run_hook",
]

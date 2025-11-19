"""Utility helpers to map user levels into allowed operations per module."""

from __future__ import annotations

from typing import Dict, List

PERMISSIONS: Dict[str, Dict[int, List[str]]] = {
    "users": {
        1: ["read", "create", "update", "delete"],
        2: [],
        3: [],
    },
    "clients": {
        1: ["read", "create", "update", "delete"],
        2: ["read", "create", "update", "delete"],
        3: ["read"],
    },
    "products": {
        1: ["read", "create", "update", "delete"],
        2: ["read", "create", "update"],
        3: ["read"],
    },
    "providers": {
        1: ["read", "create", "update", "delete"],
        2: ["read", "create", "update"],
        3: ["read"],
    },
    "inventories": {
        1: ["read", "create", "update", "delete"],
        2: ["read", "create", "update"],
        3: ["read"],
    },
    "sales": {
        1: ["read", "create", "update", "delete", "report"],
        2: ["read", "create", "update", "delete", "report"],
        3: ["read", "report"],
    },
    "reports": {
        1: ["read", "report"],
        2: ["read", "report"],
        3: ["read", "report"],
    },
}


def allowed_actions(module: str, level: int) -> List[str]:
    """Return the list of allowed actions for the module and user level."""
    module = module.lower()
    return PERMISSIONS.get(module, {}).get(level, [])
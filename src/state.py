"""Persistent state helpers for processed bid ids."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def load_state(state_path: Path) -> dict[str, Any]:
    """Load state.json or return an empty state when it does not exist."""
    if not state_path.exists():
        return {"processed_bid_ids": [], "updated_at": None}

    with state_path.open("r", encoding="utf-8") as file_obj:
        state = json.load(file_obj)
    state.setdefault("processed_bid_ids", [])
    state.setdefault("updated_at", None)
    return state


def processed_ids(state: dict[str, Any]) -> set[str]:
    """Return processed bid ids as a set."""
    return {str(item) for item in state.get("processed_bid_ids", [])}


def mark_processed(state_path: Path, state: dict[str, Any], bid_ids: list[str]) -> dict[str, Any]:
    """Persist bid ids as processed while keeping state stable across runs."""
    merged_ids = sorted(processed_ids(state).union(bid_id for bid_id in bid_ids if bid_id))
    updated_state = {
        "processed_bid_ids": merged_ids,
        "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(updated_state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return updated_state


def reset_state(state_path: Path) -> None:
    """Reset processed ids for repeatable local testing."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps({"processed_bid_ids": [], "updated_at": None}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

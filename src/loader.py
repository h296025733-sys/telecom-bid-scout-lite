"""Input loading helpers for bid candidates and scoring rules."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import yaml


def load_bids(csv_path: Path) -> list[dict[str, str]]:
    """Load bid candidates from a UTF-8 CSV file."""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def load_rules(rules_path: Path) -> dict[str, Any]:
    """Load YAML scoring rules from disk."""
    with rules_path.open("r", encoding="utf-8") as file_obj:
        rules = yaml.safe_load(file_obj) or {}

    required_keys = {
        "include_keywords",
        "exclude_keywords",
        "high_value_keywords",
        "trusted_sources",
        "min_score_follow",
        "min_score_review",
        "feishu_webhook_env",
    }
    missing_keys = sorted(required_keys.difference(rules))
    if missing_keys:
        raise ValueError(f"rules.yaml missing required keys: {', '.join(missing_keys)}")
    return rules

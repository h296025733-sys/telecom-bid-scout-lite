"""Feishu webhook notifications for follow-up bid candidates."""

from __future__ import annotations

import os
from typing import Any

import requests

from src.scorer import FOLLOW, REVIEW


def _build_message(results: list[dict[str, Any]]) -> str:
    """Build a compact Feishu text message for selected candidates."""
    lines = ["通信招采线索提醒", f"待关注线索：{len(results)} 条"]
    for result in results:
        link = result.get("official_entry") or result.get("url") or "无链接"
        lines.extend(
            [
                "",
                f"[{result['decision']}] {result.get('title', '未命名公告')}",
                f"地区：{result.get('region', '未填写')} | 截止：{result.get('deadline', '未填写')} | 评分：{result['score']}",
                f"来源：{result.get('source', '未填写')}",
                f"链接：{link}",
            ]
        )
    return "\n".join(lines)


def push_to_feishu(
    results: list[dict[str, Any]],
    webhook_env: str = "FEISHU_WEBHOOK_URL",
) -> bool:
    """Push follow and review results to Feishu without raising on failure."""
    webhook_url = os.getenv(webhook_env, "").strip()
    if not webhook_url:
        print(f"[feishu] 未配置环境变量 {webhook_env}，跳过推送。")
        return False

    selected = [result for result in results if result["decision"] in {FOLLOW, REVIEW}]
    if not selected:
        print("[feishu] 没有需要推送的线索。")
        return True

    payload = {"msg_type": "text", "content": {"text": _build_message(selected)}}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[feishu] 推送失败，主流程继续：{exc}")
        return False

    print(f"[feishu] 已推送 {len(selected)} 条线索。")
    return True

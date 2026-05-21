"""Rule-based scoring for telecom bid candidates."""

from __future__ import annotations

from datetime import date
from typing import Any

from dateutil import parser

FOLLOW = "值得跟进"
REVIEW = "需人工复核"
REJECT = "不建议跟进"


def _parse_date(raw_value: str) -> date | None:
    """Parse one date-like value and return None when it is unusable."""
    if not raw_value:
        return None
    try:
        return parser.parse(raw_value).date()
    except (TypeError, ValueError, OverflowError):
        return None


def _match_keywords(text: str, keywords: list[str]) -> list[str]:
    """Return configured keywords found in a text block."""
    lowered_text = text.lower()
    return [keyword for keyword in keywords if keyword.lower() in lowered_text]


def score_bid(
    bid: dict[str, str],
    rules: dict[str, Any],
    processed_ids: set[str] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Score one bid and explain the decision with readable reasons."""
    today = today or date.today()
    processed_ids = processed_ids or set()
    text = " ".join([bid.get("title", ""), bid.get("summary", "")])

    include_matches = _match_keywords(text, list(rules["include_keywords"]))
    exclude_matches = _match_keywords(text, list(rules["exclude_keywords"]))
    high_value_matches = _match_keywords(text, list(rules["high_value_keywords"]))
    source_matches = _match_keywords(bid.get("source", ""), list(rules["trusted_sources"]))

    publish_date = _parse_date(bid.get("publish_date", ""))
    deadline = _parse_date(bid.get("deadline", ""))
    has_url = bool(bid.get("url", ""))
    has_official_entry = bool(bid.get("official_entry", ""))
    is_duplicate = bid.get("id", "") in processed_ids

    score = 0
    reasons: list[str] = []

    if include_matches:
        score += min(30, 12 + len(include_matches) * 6)
        reasons.append(f"命中通信方向关键词：{', '.join(include_matches)}")
    else:
        score -= 18
        reasons.append("未命中明确的通信行业关键词")

    if high_value_matches:
        score += min(24, len(high_value_matches) * 8)
        reasons.append(f"命中高价值关键词：{', '.join(high_value_matches)}")

    if exclude_matches:
        score -= 35
        reasons.append(f"命中排除关键词：{', '.join(exclude_matches)}")

    if publish_date and publish_date <= today:
        score += 6
        reasons.append(f"发布时间可用：{publish_date.isoformat()}")
    else:
        score -= 10
        reasons.append("发布时间缺失、无法解析或晚于当前日期")

    if deadline and deadline >= today:
        score += 20
        reasons.append(f"仍在有效期内，截止 {deadline.isoformat()}")
    elif deadline:
        score -= 35
        reasons.append(f"公告已过期，截止 {deadline.isoformat()}")
    else:
        score -= 14
        reasons.append("截止时间缺失或无法解析")

    if source_matches:
        score += 16
        reasons.append(f"来源可信：{bid.get('source', '')}")
    else:
        score -= 8
        reasons.append(f"来源需核验：{bid.get('source', '') or '未填写'}")

    if has_official_entry:
        score += 18
        reasons.append("存在报名入口或官方公告入口")
    elif has_url:
        score += 6
        reasons.append("存在候选链接，但缺少明确官方入口")
    else:
        score -= 18
        reasons.append("缺少链接和官方入口")

    if is_duplicate:
        reasons.append("该线索已在状态文件中记录，飞书推送会跳过")

    score = max(0, min(100, score))
    if score >= int(rules["min_score_follow"]):
        decision = FOLLOW
    elif score >= int(rules["min_score_review"]):
        decision = REVIEW
    else:
        decision = REJECT

    if decision == FOLLOW and not has_official_entry:
        decision = REVIEW
        reasons.append("缺少明确官方入口，判断降级为人工复核")

    if deadline and deadline < today:
        decision = REJECT
    if exclude_matches and not include_matches:
        decision = REJECT

    matched_keywords = list(dict.fromkeys(include_matches + high_value_matches))
    return {
        **bid,
        "score": score,
        "decision": decision,
        "reasons": reasons,
        "matched_keywords": matched_keywords,
        "matched_exclude_keywords": exclude_matches,
        "is_duplicate": is_duplicate,
    }


def score_bids(
    bids: list[dict[str, str]],
    rules: dict[str, Any],
    processed_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Score every loaded candidate with the same rule set."""
    return [score_bid(bid, rules, processed_ids=processed_ids) for bid in bids]

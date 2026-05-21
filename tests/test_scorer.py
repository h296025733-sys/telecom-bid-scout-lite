"""Unit tests for the rule-based bid scorer."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path

from src.loader import load_rules
from src.scorer import FOLLOW, REJECT, REVIEW, score_bid


BASE_DIR = Path(__file__).resolve().parents[1]
RULES_PATH = BASE_DIR / "config" / "rules.yaml"
TEST_TODAY = date(2026, 5, 21)


def make_bid(**overrides: str) -> dict[str, str]:
    """Build one valid bid fixture with focused overrides."""
    bid = {
        "id": "TEST-001",
        "title": "通信服务采购公告",
        "publish_date": "2026-05-10",
        "deadline": "2026-06-10",
        "region": "北京",
        "source": "公共资源交易中心",
        "url": "https://example.org/bids/test",
        "summary": "采购通信服务能力",
        "official_entry": "https://example.org/official/test",
    }
    bid.update(overrides)
    return bid


class ScorerTests(unittest.TestCase):
    """Validate key rule outcomes exposed by scorer.py."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load project rules once for all scorer tests."""
        cls.rules = load_rules(RULES_PATH)

    def test_contact_center_and_voice_line_can_be_followed(self) -> None:
        """High-value telecom leads should reach the follow bucket."""
        bid = make_bid(
            title="呼叫中心外呼系统与语音线路采购公告",
            summary="采购呼叫中心坐席、外呼系统和语音线路接入能力",
        )

        result = score_bid(bid, self.rules, today=TEST_TODAY)

        self.assertEqual(FOLLOW, result["decision"])
        self.assertIn("呼叫中心", result["matched_keywords"])
        self.assertIn("语音线路", result["matched_keywords"])

    def test_unrelated_printer_canteen_property_bid_is_rejected(self) -> None:
        """Office and property noise should not enter the follow queue."""
        bid = make_bid(
            title="打印机、物业与食堂服务采购公告",
            summary="采购打印机耗材、物业保洁和食堂服务",
        )

        result = score_bid(bid, self.rules, today=TEST_TODAY)

        self.assertEqual(REJECT, result["decision"])
        self.assertGreaterEqual(len(result["matched_exclude_keywords"]), 3)

    def test_expired_bid_is_not_high_priority(self) -> None:
        """Expired telecom bids must be rejected even with good signals."""
        bid = make_bid(
            title="语音线路和SIP中继资源采购公告",
            summary="采购语音线路和SIP中继",
            publish_date="2025-03-01",
            deadline="2025-03-20",
        )

        result = score_bid(bid, self.rules, today=TEST_TODAY)

        self.assertEqual(REJECT, result["decision"])
        self.assertNotEqual(FOLLOW, result["decision"])

    def test_missing_official_entry_downgrades_related_bid_to_review(self) -> None:
        """Business-relevant leads without official entry need review."""
        bid = make_bid(
            title="语音线路资源采购公告",
            summary="采购语音线路和通信服务",
            official_entry="",
        )

        result = score_bid(bid, self.rules, today=TEST_TODAY)

        self.assertEqual(REVIEW, result["decision"])
        self.assertIn("缺少明确官方入口，判断降级为人工复核", result["reasons"])

    def test_high_value_keyword_increases_score(self) -> None:
        """High-value keywords should add score above a normal include word."""
        normal_bid = make_bid(
            id="TEST-NORMAL",
            title="通信服务采购公告",
            summary="采购通信服务能力",
        )
        high_value_bid = make_bid(
            id="TEST-HIGH",
            title="语音线路采购公告",
            summary="采购语音线路能力",
        )

        normal_result = score_bid(normal_bid, self.rules, today=TEST_TODAY)
        high_value_result = score_bid(high_value_bid, self.rules, today=TEST_TODAY)

        self.assertGreater(high_value_result["score"], normal_result["score"])


if __name__ == "__main__":
    unittest.main()

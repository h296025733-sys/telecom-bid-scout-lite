"""Command line entrypoint for telecom-bid-scout-lite."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from src.feishu import push_to_feishu
from src.loader import load_bids, load_rules
from src.reporter import write_report
from src.scorer import FOLLOW, REVIEW, score_bids
from src.state import load_state, mark_processed, processed_ids, reset_state

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sample_bids.csv"
RULES_PATH = BASE_DIR / "config" / "rules.yaml"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_PATH = OUTPUT_DIR / "report.md"
STATE_PATH = OUTPUT_DIR / "state.json"

LOGGER = logging.getLogger("telecom_bid_scout")


def run_pipeline(no_feishu: bool = False) -> None:
    """Run the full load, score, report, notify, and state workflow."""
    LOGGER.info("读取候选招采数据：%s", DATA_PATH)
    bids = load_bids(DATA_PATH)
    LOGGER.info("加载规则配置：%s", RULES_PATH)
    rules = load_rules(RULES_PATH)

    state = load_state(STATE_PATH)
    seen_ids = processed_ids(state)
    LOGGER.info("当前状态中已有 %s 条已处理线索。", len(seen_ids))

    results = score_bids(bids, rules, processed_ids=seen_ids)
    report_path = write_report(results, REPORT_PATH)
    LOGGER.info("报告已生成：%s", report_path)

    pushable_results = [
        result
        for result in results
        if result["decision"] in {FOLLOW, REVIEW} and not result["is_duplicate"]
    ]
    if no_feishu:
        LOGGER.info("已按参数跳过飞书推送。")
    else:
        LOGGER.info("准备推送 %s 条未重复的待关注线索。", len(pushable_results))
        push_to_feishu(pushable_results, webhook_env=str(rules["feishu_webhook_env"]))

    mark_processed(STATE_PATH, state, [result.get("id", "") for result in results])
    LOGGER.info("状态已更新：%s", STATE_PATH)


def build_parser() -> argparse.ArgumentParser:
    """Build command line arguments for the project."""
    parser = argparse.ArgumentParser(description="通信行业招采线索筛选与飞书推送工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="执行完整筛选流程")
    run_parser.add_argument("--no-feishu", action="store_true", help="跳过飞书推送")
    subparsers.add_parser("reset-state", help="清空 outputs/state.json")
    return parser


def main() -> None:
    """Dispatch CLI commands."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    args = build_parser().parse_args()
    if args.command == "run":
        run_pipeline(no_feishu=args.no_feishu)
    elif args.command == "reset-state":
        reset_state(STATE_PATH)
        LOGGER.info("状态已清空：%s", STATE_PATH)


if __name__ == "__main__":
    main()

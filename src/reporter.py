"""Markdown report generation for scored bid candidates."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from src.scorer import FOLLOW, REJECT, REVIEW


def _display(raw_value: str, fallback: str = "未填写") -> str:
    """Return a printable value for reports."""
    return raw_value or fallback


def build_report(results: list[dict[str, Any]]) -> str:
    """Build a Markdown report from scored bid results."""
    counts = Counter(result["decision"] for result in results)
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# 通信行业招采线索筛选报告",
        "",
        f"- 报告生成时间：{generated_at}",
        f"- 总线索数量：{len(results)}",
        f"- 值得跟进数量：{counts[FOLLOW]}",
        f"- 需人工复核数量：{counts[REVIEW]}",
        f"- 不建议跟进数量：{counts[REJECT]}",
        "",
        "## 线索明细",
        "",
    ]

    for index, result in enumerate(results, start=1):
        keywords = "、".join(result["matched_keywords"]) or "无"
        reasons = "；".join(result["reasons"])
        link = result.get("official_entry") or result.get("url") or "未填写"
        lines.extend(
            [
                f"### {index}. {_display(result.get('title', ''))}",
                "",
                f"- 地区：{_display(result.get('region', ''))}",
                f"- 来源：{_display(result.get('source', ''))}",
                f"- 截止时间：{_display(result.get('deadline', ''))}",
                f"- 判断结果：**{result['decision']}**",
                f"- 评分：{result['score']}",
                f"- 命中关键词：{keywords}",
                f"- 判断原因：{reasons}",
                f"- 链接：{link}",
                "",
            ]
        )

    lines.extend(
        [
            "## 适合 OpenClaw 调用方式",
            "",
            "OpenClaw 可以负责定时搜索、网页读取和候选公告整理，再把候选数据写入 CSV 后调用：",
            "",
            "```bash",
            "python main.py run",
            "```",
            "",
            "本项目随后负责可解释规则打分、状态去重、Markdown 报告生成和可选飞书推送。",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(results: list[dict[str, Any]], output_path: Path) -> Path:
    """Write the Markdown report to the output directory."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_report(results), encoding="utf-8")
    return output_path

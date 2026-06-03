#!/usr/bin/env python3
"""myco_cycle.py — 知识系统代谢循环追踪器

从 Myco 认知基质框架的 cycle 子系统提取设计模式，
追踪 knowledge-system 四步管线（摄取→消化→输出→巡检）的执行节奏。

用法:
  python tools/myco_cycle.py                  # 默认：显示当前循环状态
  python tools/myco_cycle.py --stage ingest   # 标记摄取完成
  python tools/myco_cycle.py --stage digest   # 标记消化完成
  python tools/myco_cycle.py --stage output   # 标记输出完成
  python tools/myco_cycle.py --stage inspect  # 标记巡检完成
  python tools/myco_cycle.py --report         # 生成循环健康报告
  python tools/myco_cycle.py --close          # 关闭当前循环，开启新循环
  python tools/myco_cycle.py --history        # 查看历史循环列表
  python tools/myco_cycle.py --reset          # 重置所有状态（需确认）
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# 配置常量
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / ".myco"
STATE_FILE = STATE_DIR / "cycle_state.json"

STALL_WARN_DAYS = 2
STALL_CRITICAL_DAYS = 5

STAGES = ["ingest", "digest", "output", "inspect"]
STAGE_LABELS = {"ingest": "摄取", "digest": "消化", "output": "输出", "inspect": "巡检"}
STAGE_DIRS = {
    "ingest": REPO_ROOT / "raw",
    "digest": REPO_ROOT / "knowledge",
    "output": REPO_ROOT / "outputs",
    "inspect": REPO_ROOT / "inspection",
}

INSPECTION_DIR = REPO_ROOT / "inspection"


# ============================================================
# 状态管理
# ============================================================

def default_state() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "current_cycle_start": today,
        "stages": {
            stage: {"last_activity": None, "files_recorded": 0}
            for stage in STAGES
        },
        "history": [],
        "next_cycle_id": 1,
    }


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)
        # 确保所有字段存在
        if "stages" not in state:
            state["stages"] = {}
        for stage in STAGES:
            if stage not in state["stages"]:
                state["stages"][stage] = {"last_activity": None, "files_recorded": 0}
        if "history" not in state:
            state["history"] = []
        if "current_cycle_start" not in state:
            state["current_cycle_start"] = datetime.now().strftime("%Y-%m-%d")
        if "next_cycle_id" not in state:
            state["next_cycle_id"] = 1
        return state
    except (FileNotFoundError, json.JSONDecodeError):
        return default_state()


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ============================================================
# 工具函数
# ============================================================

def count_md_files(directory: Path) -> int:
    """递归统计 .md 文件数。"""
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.rglob("*.md"))


def stall_days(stage: str, state: dict) -> int:
    """计算某阶段的停滞天数。"""
    last = state["stages"][stage]["last_activity"]
    if not last:
        # 从未标记过，从循环开始算
        try:
            start = datetime.strptime(state["current_cycle_start"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - start).days
        except (ValueError, KeyError):
            return 0
    try:
        dt = datetime.fromisoformat(last)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except (ValueError, TypeError):
        return 0


def stall_status(days: int) -> str:
    """停滞状态标记。"""
    if days <= STALL_WARN_DAYS:
        return "✅ 活跃"
    elif days < STALL_CRITICAL_DAYS:
        return "⚠️ 轻微停滞"
    else:
        return "🔴 严重停滞"


def count_new_files(stage: str, state: dict) -> int:
    """对比实际文件数与已记录数的差异。"""
    recorded = state["stages"][stage].get("files_recorded", 0)
    actual = count_md_files(STAGE_DIRS.get(stage, REPO_ROOT))
    return max(0, actual - recorded)


# ============================================================
# 命令实现
# ============================================================

def cmd_status(state: dict) -> None:
    """默认输出：显示当前循环状态。"""
    cycle_id = state.get("next_cycle_id", 1)
    start = state.get("current_cycle_start", "?")
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - start_dt).days
    except (ValueError, TypeError):
        elapsed = 0

    print(f"代谢循环 #{cycle_id}")
    print(f"周期开始：{start}")
    print(f"距今：{elapsed} 天")
    print()
    print(f"{'阶段':<8} {'最后活跃':<24} {'停滞天数':<10} {'状态'}")
    print("-" * 60)

    for stage in STAGES:
        last = state["stages"][stage]["last_activity"]
        label = STAGE_LABELS.get(stage, stage)
        if last:
            try:
                dt = datetime.fromisoformat(last)
                display = dt.strftime("%Y-%m-%dT%H:%M:%S")
            except (ValueError, TypeError):
                display = last
        else:
            display = "—"
        days = stall_days(stage, state)
        status = stall_status(days)
        print(f"{label:<8} {display:<24} {days:<10} {status}")

    print()
    # 数据流
    ing = count_new_files("ingest", state)
    dig = count_new_files("digest", state)
    out = count_new_files("output", state)
    print(f"数据流：")
    print(f"  摄取({state['stages']['ingest']['files_recorded']}+{ing}) → "
          f"消化({state['stages']['digest']['files_recorded']}+{dig}) → "
          f"输出({state['stages']['output']['files_recorded']}+{out})")

    warnings = []
    if ing > 0:
        warnings.append(f"  ⚠️  {ing} 个 raw 文件未被 cycle 记录")
    if dig > 0:
        warnings.append(f"  ⚠️  {dig} 个 knowledge 文件未被 cycle 记录")
    if warnings:
        for w in warnings:
            print(w)


def cmd_stage(stage: str, state: dict) -> None:
    """标记某阶段完成。"""
    now = datetime.now(timezone.utc).isoformat()
    state["stages"][stage]["last_activity"] = now
    state["stages"][stage]["files_recorded"] = count_md_files(STAGE_DIRS.get(stage, REPO_ROOT))
    save_state(state)
    print(f"✅ {STAGE_LABELS.get(stage, stage)}阶段已标记 "
          f"（{state['stages'][stage]['files_recorded']} 个文件）")


def cmd_report(state: dict) -> None:
    """生成循环健康报告。"""
    today = datetime.now().strftime("%Y-%m-%d")
    cycle_id = state.get("next_cycle_id", 1)
    start = state.get("current_cycle_start", "?")
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - start_dt).days
    except (ValueError, TypeError):
        elapsed = 0

    lines: List[str] = []
    lines.append(f"# 代谢循环报告 — Cycle #{cycle_id}")
    lines.append("")
    lines.append(f"> 周期：{start} ~ 至今（第 {elapsed} 天）")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # 阶段状态表
    lines.append("## 阶段状态")
    lines.append("")
    lines.append("| 阶段 | 最后活跃 | 停滞天数 | 状态 |")
    lines.append("|------|---------|---------|------|")
    for stage in STAGES:
        label = STAGE_LABELS.get(stage, stage)
        last = state["stages"][stage]["last_activity"]
        if last:
            try:
                dt = datetime.fromisoformat(last)
                display = dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                display = last
        else:
            display = "—"
        days = stall_days(stage, state)
        status = stall_status(days)
        status_text = status.split(" ", 1)[1] if " " in status else status
        lines.append(f"| {label} | {display} | {days} 天 | {status_text} |")
    lines.append("")

    # 数据流
    lines.append("## 数据流")
    lines.append("")
    ing_f = state["stages"]["ingest"]["files_recorded"]
    dig_f = state["stages"]["digest"]["files_recorded"]
    out_f = state["stages"]["output"]["files_recorded"]
    lines.append(f"摄取({ing_f}) → 消化({dig_f}) → 输出({out_f})")
    lines.append("")

    # 建议
    lines.append("## 建议")
    lines.append("")
    suggestions = []
    for stage in STAGES:
        days = stall_days(stage, state)
        label = STAGE_LABELS.get(stage, stage)
        if days >= STALL_CRITICAL_DAYS:
            suggestions.append(f"- {label}阶段停滞 {days} 天，建议立即处理")
        elif days >= STALL_WARN_DAYS:
            suggestions.append(f"- {label}阶段有积压，建议优先处理")
    for stage in STAGES:
        new = count_new_files(stage, state)
        if new > 0:
            suggestions.append(f"- 发现 {new} 个未记录的 {STAGE_LABELS.get(stage, stage)} 文件，可能被手动放入")
    if not suggestions:
        suggestions.append("- 所有阶段运行正常，继续保持。")
    lines.extend(suggestions)
    lines.append("")

    report = "\n".join(lines)
    print(report)

    # 写入 inspection/
    INSPECTION_DIR.mkdir(parents=True, exist_ok=True)
    report_path = INSPECTION_DIR / f"{today}-cycle-report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"📄 报告已保存: {report_path.relative_to(REPO_ROOT)}")


def cmd_close(state: dict) -> None:
    """关闭当前循环，归档并开启新循环。"""
    stages = state["stages"]
    summary_parts = []
    for stage in STAGES:
        label = STAGE_LABELS.get(stage, stage)
        count = stages[stage]["files_recorded"]
        summary_parts.append(f"{count} 次{label}")
    summary = "完成 " + "、".join(summary_parts)

    # 归档
    archive = {
        "cycle_id": state.get("next_cycle_id", 1),
        "start": state["current_cycle_start"],
        "end": datetime.now().strftime("%Y-%m-%d"),
        "summary": summary,
    }
    state["history"].append(archive)

    # 重置
    today = datetime.now().strftime("%Y-%m-%d")
    state["current_cycle_start"] = today
    state["stages"] = {
        stage: {"last_activity": None, "files_recorded": 0}
        for stage in STAGES
    }
    state["next_cycle_id"] = state.get("next_cycle_id", 1) + 1

    save_state(state)
    print(f"✅ Cycle #{archive['cycle_id']} 已关闭并归档")
    print(f"   摘要：{summary}")
    print(f"   新循环 #{state['next_cycle_id']} 已开始 ({today})")


def cmd_history(state: dict) -> None:
    """查看历史循环列表。"""
    history = state.get("history", [])
    if not history:
        print("暂无历史循环记录。")
        return
    print(f"历史循环（共 {len(history)} 个）：")
    print("-" * 60)
    for h in history:
        print(f"  Cycle #{h.get('cycle_id', '?')}: {h.get('start', '?')} ~ {h.get('end', '?')}")
        print(f"    {h.get('summary', '')}")
        print()


def cmd_reset(state: dict) -> None:
    """重置所有状态（需确认）。"""
    print("⚠️  这将删除所有循环状态和历史记录！")
    resp = input("确认重置？(y/N): ").strip().lower()
    if resp == "y" or resp == "yes":
        new_state = default_state()
        save_state(new_state)
        print("✅ 状态已重置")
    else:
        print("已取消")


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="myco_cycle — 知识系统代谢循环追踪器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/myco_cycle.py                    # 显示当前循环状态
  python tools/myco_cycle.py --stage ingest     # 标记摄取完成
  python tools/myco_cycle.py --report           # 生成循环健康报告
  python tools/myco_cycle.py --close            # 关闭当前循环
  python tools/myco_cycle.py --history          # 查看历史
        """,
    )
    parser.add_argument(
        "--stage",
        choices=STAGES,
        help="标记某阶段完成",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成循环健康报告 → inspection/",
    )
    parser.add_argument(
        "--close",
        action="store_true",
        help="关闭当前循环，归档并开启新循环",
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="查看历史循环列表",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置所有状态（需确认）",
    )

    args = parser.parse_args()
    state = load_state()

    if args.stage:
        cmd_stage(args.stage, state)
    elif args.report:
        cmd_report(state)
    elif args.close:
        cmd_close(state)
    elif args.history:
        cmd_history(state)
    elif args.reset:
        cmd_reset(state)
    else:
        cmd_status(state)


if __name__ == "__main__":
    main()

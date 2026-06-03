#!/usr/bin/env python3
"""myco_immune.py — 知识系统免疫检查器

从 Myco 认知基质框架的 homeostasis 子系统提取核心检查逻辑，
以纯 Python 标准库实现四维知识库健康检查。

4 维检查:
  MB1_RawBacklog    — raw/ 目录原料积压检测
  MB2_NoIntegrated  — knowledge/ 条目未被引用检测
  SE1_DanglingRefs  — [[wikilink]] 断链检测
  SE2_OrphanIntegrated — 元数据缺失检测

用法:
  python tools/myco_immune.py              # 默认：完整 Markdown 报告
  python tools/myco_immune.py --summary    # 一行摘要 + exit_code
  python tools/myco_immune.py --json       # JSON 格式给 Agent 消费
  python tools/myco_immune.py --fix        # 自动修复断链
  python tools/myco_immune.py --categories semantic  # 只跑语义检查
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ============================================================
# 类型系统
# ============================================================

class Severity(IntEnum):
    """严重级别，数值越大越严重。Agent 可直接比较数值做决策。"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return self.name


class Category(str, Enum):
    """检查维度分类"""
    METABOLIC = "metabolic"
    SEMANTIC = "semantic"


# ============================================================
# 配置常量
# ============================================================

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "raw"
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
INSPECTION_DIR = REPO_ROOT / "inspection"
STATE_DIR = REPO_ROOT / ".myco"
STATE_FILE = STATE_DIR / "immune_state.json"

DEFAULT_MAX_AGE_DAYS = 7
CRITICAL_AGE_DAYS = 14

# 跳过的目录（不检查 wikilink）
SKIP_DIRS = {".git", ".obsidian", ".myco", "inspection", "__pycache__"}

# wikilink 正则: [[target]] 或 [[target|alias]]
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")


# ============================================================
# 状态管理
# ============================================================

def default_state() -> dict:
    return {"last_run": None, "acknowledged": {"MB1": [], "SE1": []}}


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_state()


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


# ============================================================
# 工具函数
# ============================================================

def parse_frontmatter(text: str) -> dict:
    """解析 YAML frontmatter（简单实现：--- 之间的 key: value 行）。"""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            fm[key.strip()] = val
    return fm


def extract_wikilinks(text: str) -> List[str]:
    """提取文本中所有 [[wikilink]] 目标的 stem。"""
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]


def file_age_days(filepath: Path) -> int:
    """计算文件距今多少天。"""
    mtime = filepath.stat().st_mtime
    now = datetime.now().timestamp()
    return int((now - mtime) / 86400)


def count_md_files(directory: Path) -> int:
    """递归统计 .md 文件数。"""
    if not directory.exists():
        return 0
    return sum(1 for _ in directory.rglob("*.md"))


def date_from_filename(filename: str) -> Optional[str]:
    """从文件名提取 YYYY-MM-DD 格式日期。"""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filename)
    return m.group(1) if m else None


def to_page_stem(path: Path, root: Path) -> str:
    """将文件路径转换为页面标识（相对路径去掉 .md 后缀）。"""
    rel = path.relative_to(root)
    return str(rel.with_suffix(""))


# ============================================================
# 索引函数（性能优化）
# ============================================================

def _build_wikilink_index(root: Path) -> Tuple[Set[str], Dict[str, List[str]]]:
    """一次扫描构建全仓库 wikilink 索引。

    Returns:
        all_pages: 仓库中所有 .md 文件的页面 stem 集合
        page_links: {page_stem: [linked_target, ...]}  每页引用了哪些页面
    """
    all_pages: Set[str] = set()
    page_links: Dict[str, List[str]] = {}

    for md_file in root.rglob("*.md"):
        # 跳过特殊目录
        parts = set(md_file.relative_to(root).parts)
        if parts & SKIP_DIRS:
            continue

        stem = to_page_stem(md_file, root)
        all_pages.add(stem)

        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            links = extract_wikilinks(text)
            if links:
                page_links[stem] = links
        except Exception:
            continue

    return all_pages, page_links


# ============================================================
# 检查函数
# ============================================================

def check_MB1(max_age: int, state: dict) -> List[dict]:
    """MB1 — RawBacklog：raw/ 目录原料积压检测。"""
    findings = []
    acknowledged = set(state.get("acknowledged", {}).get("MB1", []))

    if not RAW_DIR.exists():
        return findings

    for md_file in RAW_DIR.iterdir():
        if not md_file.is_file() or not md_file.suffix == ".md":
            continue

        rel = str(md_file.relative_to(REPO_ROOT))
        if rel in acknowledged:
            continue

        # 优先从文件名提取日期，失败则用文件修改时间
        date_str = date_from_filename(md_file.name)
        if date_str:
            try:
                file_dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - file_dt).days
            except ValueError:
                age = file_age_days(md_file)
        else:
            age = file_age_days(md_file)

        if age > max_age:
            severity = Severity.HIGH if age >= CRITICAL_AGE_DAYS else Severity.MEDIUM
            findings.append({
                "dimension": "MB1_RawBacklog",
                "category": Category.METABOLIC.value,
                "severity": int(severity),
                "severity_label": severity.label,
                "file": rel,
                "age_days": age,
                "message": f"raw/ 原料 '{md_file.name}' 已积压 {age} 天（阈值 {max_age} 天）",
                "suggestion": "尽快消化或确认不再需要后移入归档",
                "fixable": False,
            })

    return findings


def check_MB2(state: dict, wikilink_index: Tuple[Set[str], Dict[str, List[str]]]) -> List[dict]:
    """MB2 — NoIntegrated：knowledge/ 中未被引用的孤立条目。"""
    findings = []
    all_pages, page_links = wikilink_index

    # 构建被引用集合（检查所有链接目标是否在 knowledge/ 下）
    referenced: Set[str] = set()
    for source, targets in page_links.items():
        for target in targets:
            referenced.add(target)

    if not KNOWLEDGE_DIR.exists():
        return findings

    for md_file in KNOWLEDGE_DIR.rglob("*.md"):
        stem = to_page_stem(md_file, KNOWLEDGE_DIR)
        if stem not in referenced:
            # 也排除自身引用自身的情况
            if stem in page_links:
                continue
            rel = str(md_file.relative_to(REPO_ROOT))
            findings.append({
                "dimension": "MB2_NoIntegrated",
                "category": Category.METABOLIC.value,
                "severity": int(Severity.LOW),
                "severity_label": Severity.LOW.label,
                "file": rel,
                "target": stem,
                "message": f"knowledge/ 条目 '{stem}' 未被任何文件引用",
                "suggestion": "考虑添加引用链接或评估是否需要保留该条目",
                "fixable": False,
            })

    return findings


def check_SE1(state: dict, wikilink_index: Tuple[Set[str], Dict[str, List[str]]]) -> List[dict]:
    """SE1 — DanglingRefs：[[wikilink]] 断链检测。"""
    findings = []
    all_pages, page_links = wikilink_index

    # 构建已确认的断链集合（用 {file, target} 做 key，不用行号）
    ack_set: Set[Tuple[str, str]] = set()
    for ack in state.get("acknowledged", {}).get("SE1", []):
        if isinstance(ack, dict):
            ack_set.add((ack.get("file", ""), ack.get("target", "")))

    for source_stem, targets in page_links.items():
        # 找到源文件路径
        source_md = None
        candidate1 = REPO_ROOT / (source_stem + ".md")
        candidate2 = KNOWLEDGE_DIR / (source_stem + ".md")
        if candidate1.exists():
            source_md = candidate1
        elif candidate2.exists():
            source_md = candidate2
        else:
            # 尝试在仓库内搜索
            for ext_dir in [REPO_ROOT, KNOWLEDGE_DIR]:
                for f in ext_dir.rglob("*.md"):
                    if to_page_stem(f, ext_dir) == source_stem:
                        source_md = f
                        break
                if source_md:
                    break
        if not source_md:
            continue

        for target in set(targets):
            # 断链判定：target 不在 all_pages 中
            if target not in all_pages:
                rel = str(source_md.relative_to(REPO_ROOT))
                key = (rel, target)
                if key in ack_set:
                    continue

                # 找到行号
                line_num = 0
                try:
                    text = source_md.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(text.split("\n"), 1):
                        if f"[[{target}" in line or f"[[{target}|" in line or f"[[{target}#" in line:
                            line_num = i
                            break
                except Exception:
                    pass

                findings.append({
                    "dimension": "SE1_DanglingRefs",
                    "category": Category.SEMANTIC.value,
                    "severity": int(Severity.HIGH),
                    "severity_label": Severity.HIGH.label,
                    "file": rel,
                    "line": line_num,
                    "target": target,
                    "message": f"[[{target}]] 指向不存在的文件",
                    "suggestion": "删除断链或创建目标文件",
                    "fixable": True,
                })

    return findings


def check_SE2() -> List[dict]:
    """SE2 — OrphanIntegrated：knowledge/ 文件缺少元数据字段。"""
    findings = []

    if not KNOWLEDGE_DIR.exists():
        return findings

    for md_file in KNOWLEDGE_DIR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        fm = parse_frontmatter(text)
        missing = []
        if not fm.get("sources"):
            missing.append("sources")
        if not fm.get("related"):
            missing.append("related")

        if missing:
            rel = str(md_file.relative_to(REPO_ROOT))
            severity = Severity.MEDIUM if len(missing) >= 2 else Severity.LOW
            findings.append({
                "dimension": "SE2_OrphanIntegrated",
                "category": Category.SEMANTIC.value,
                "severity": int(severity),
                "severity_label": severity.label,
                "file": rel,
                "missing_fields": missing,
                "message": f"knowledge/ 条目缺少元数据字段: {', '.join(missing)}",
                "suggestion": f"在 frontmatter 中添加 {', '.join(missing)} 字段",
                "fixable": False,
            })

    return findings


# ============================================================
# 修复函数
# ============================================================

def fix_SE1(findings: List[dict]) -> int:
    """修复 SE1 断链：将 [[broken-link]] 替换为纯文本 broken-link。"""
    fixed_count = 0
    # 按文件分组
    by_file: Dict[str, List[str]] = {}
    for f in findings:
        if f["dimension"] == "SE1_DanglingRefs" and f["fixable"]:
            by_file.setdefault(f["file"], []).append(f["target"])

    for rel_path, targets in by_file.items():
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue
        text = file_path.read_text(encoding="utf-8")
        original = text
        for target in targets:
            # 替换 [[target]] → target
            text = re.sub(rf"\[\[{re.escape(target)}\]\]", target, text)
            # 替换 [[target|alias]] → alias
            text = re.sub(rf"\[\[{re.escape(target)}\|([^\]]+)\]\]", r"\1", text)
        if text != original:
            file_path.write_text(text, encoding="utf-8")
            fixed_count += 1

    return fixed_count


# ============================================================
# 退出策略
# ============================================================

def compute_exit_code(findings: List[dict]) -> int:
    """CRITICAL → 2, HIGH → 1, 其他 → 0"""
    severities = {f["severity"] for f in findings}
    if int(Severity.CRITICAL) in severities:
        return 2
    if int(Severity.HIGH) in severities:
        return 1
    return 0


# ============================================================
# 检查注册表
# ============================================================

CHECK_REGISTRY: Dict[str, List[Callable]] = {
    "metabolic": [check_MB1, check_MB2],
    "semantic": [check_SE1, check_SE2],
}


# ============================================================
# 输出函数
# ============================================================

def print_report(findings: List[dict], state: dict) -> None:
    """输出 Markdown 报告到 inspection/ 并打印到 stdout。"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines: List[str] = []

    lines.append(f"# 免疫检查报告 — {today}")
    lines.append("")
    lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> 发现数量：{len(findings)}")
    lines.append("")

    if not findings:
        lines.append("✅ **无问题发现，知识库健康。**")
        lines.append("")
    else:
        # 按分类分组
        metabolic = [f for f in findings if f["category"] == Category.METABOLIC.value]
        semantic = [f for f in findings if f["category"] == Category.SEMANTIC.value]

        for cat_label, cat_findings in [("Metabolic (代谢)", metabolic), ("Semantic (语义)", semantic)]:
            if not cat_findings:
                continue
            lines.append(f"## {cat_label}")
            lines.append("")
            for f in sorted(cat_findings, key=lambda x: (-x["severity"], x.get("file", ""))):
                lines.append(f"### {f['dimension']} — {f['severity_label']} (severity={f['severity']})")
                lines.append("")
                lines.append(f"- **文件**：`{f.get('file', 'N/A')}`")
                if f.get("line"):
                    lines.append(f"- **行号**：{f['line']}")
                if f.get("target"):
                    lines.append(f"- **目标**：`{f['target']}`")
                if f.get("age_days"):
                    lines.append(f"- **积压天数**：{f['age_days']} 天")
                if f.get("missing_fields"):
                    lines.append(f"- **缺失字段**：{', '.join(f['missing_fields'])}")
                lines.append(f"- **问题**：{f['message']}")
                lines.append(f"- **建议**：{f['suggestion']}")
                if f.get("fixable"):
                    lines.append(f"- **可修复**：是（使用 `--fix` 自动修复）")
                lines.append("")

    # 统计摘要表
    lines.append("---")
    lines.append("")
    lines.append("## 统计")
    lines.append("")
    lines.append("| 维度 | Critical | High | Medium | Low | 合计 |")
    lines.append("|------|----------|------|--------|-----|------|")
    dims = ["MB1_RawBacklog", "MB2_NoIntegrated", "SE1_DanglingRefs", "SE2_OrphanIntegrated"]
    for dim in dims:
        dim_f = [f for f in findings if f["dimension"] == dim]
        c = sum(1 for f in dim_f if f["severity"] == 4)
        h = sum(1 for f in dim_f if f["severity"] == 3)
        m = sum(1 for f in dim_f if f["severity"] == 2)
        l = sum(1 for f in dim_f if f["severity"] == 1)
        lines.append(f"| {dim} | {c} | {h} | {m} | {l} | {len(dim_f)} |")
    lines.append("")
    lines.append(f"**exit_code**: {compute_exit_code(findings)}")
    lines.append("")

    report = "\n".join(lines)
    print(report)

    # 写入 inspection/
    INSPECTION_DIR.mkdir(parents=True, exist_ok=True)
    report_path = INSPECTION_DIR / f"{today}-immune-report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"📄 报告已保存: {report_path.relative_to(REPO_ROOT)}")


def print_json(findings: List[dict]) -> None:
    """JSON 格式输出。"""
    print(json.dumps(findings, indent=2, ensure_ascii=False))


def print_summary(findings: List[dict]) -> None:
    """一行摘要输出。"""
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for f in findings:
        severity_counts[f["severity"]] = severity_counts.get(f["severity"], 0) + 1

    metabolic_f = [f for f in findings if f["category"] == Category.METABOLIC.value]
    semantic_f = [f for f in findings if f["category"] == Category.SEMANTIC.value]

    def cat_summary(fs):
        sc = {1: 0, 2: 0, 3: 0, 4: 0}
        for f in fs:
            sc[f["severity"]] = sc.get(f["severity"], 0) + 1
        return f"H{sc[3]} M{sc[2]} L{sc[1]}"

    exit_code = compute_exit_code(findings)
    line = (
        f"[myco_immune] "
        f"exit_code={exit_code} | "
        f"{len(findings)} findings | "
        f"critical={severity_counts[4]} "
        f"high={severity_counts[3]} "
        f"medium={severity_counts[2]} "
        f"low={severity_counts[1]} | "
        f"metabolic: {cat_summary(metabolic_f)} | "
        f"semantic: {cat_summary(semantic_f)}"
    )
    print(line)


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="myco_immune — 知识系统免疫检查器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python tools/myco_immune.py                  # 完整 Markdown 报告
  python tools/myco_immune.py --summary        # 一行摘要
  python tools/myco_immune.py --json           # JSON 输出
  python tools/myco_immune.py --fix            # 自动修复断链
  python tools/myco_immune.py --categories semantic  # 只跑语义检查
  python tools/myco_immune.py --max-age 14     # 放宽积压阈值
        """,
    )
    parser.add_argument("--summary", action="store_true", help="只输出一行摘要")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--fix", action="store_true", help="自动修复断链（SE1）")
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=["metabolic", "semantic"],
        default=["metabolic", "semantic"],
        help="指定要运行的检查分类（默认：全部）",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=DEFAULT_MAX_AGE_DAYS,
        help=f"MB1 积压阈值（天），默认 {DEFAULT_MAX_AGE_DAYS}",
    )

    args = parser.parse_args()

    # 加载状态
    state = load_state()

    # 构建 wikilink 索引（SE1/MB2 共用）
    all_pages, page_links = _build_wikilink_index(REPO_ROOT)
    wikilink_index = (all_pages, page_links)

    # 运行选中的检查
    all_findings: List[dict] = []
    for cat in args.categories:
        for check_fn in CHECK_REGISTRY.get(cat, []):
            if check_fn is check_MB1:
                all_findings.extend(check_MB1(args.max_age, state))
            elif check_fn is check_MB2:
                all_findings.extend(check_MB2(state, wikilink_index))
            elif check_fn is check_SE1:
                all_findings.extend(check_SE1(state, wikilink_index))
            elif check_fn is check_SE2:
                all_findings.extend(check_SE2())

    # 修复模式
    if args.fix:
        fixed = fix_SE1(all_findings)
        if fixed > 0:
            print(f"✅ 已修复 {fixed} 个文件中的断链", file=sys.stderr)
            # 修复后重新运行 SE1 检查
            all_pages, page_links = _build_wikilink_index(REPO_ROOT)
            wikilink_index = (all_pages, page_links)
            all_findings = [
                f for f in all_findings if f["dimension"] != "SE1_DanglingRefs"
            ]
            all_findings.extend(check_SE1(state, wikilink_index))
        else:
            print("ℹ️  没有可自动修复的断链", file=sys.stderr)

    # 保存状态
    save_state(state)

    # 输出
    if args.summary:
        print_summary(all_findings)
    elif args.json:
        print_json(all_findings)
    else:
        print_report(all_findings, state)

    # 退出码
    sys.exit(compute_exit_code(all_findings))


if __name__ == "__main__":
    main()

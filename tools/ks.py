"""
知识系统 CLI 工具 — TRAE 操作入口（升级版）。

支持双模式运行：
    - REST API 模式：通过 Obsidian Local REST API 与 Obsidian 深度交互
    - Local 模式：直接操作文件系统，无需 Obsidian 运行

自动检测 Obsidian 可用性，智能切换模式。
封装知识系统四步流程：摄取 → 消化 → 输出 → 巡检。

用法：
    # 基础操作
    python tools/ks.py status                           # 查看连接状态
    python tools/ks.py health                           # 健康检查
    python tools/ks.py search "关键词"                   # 搜索
    python tools/ks.py read knowledge/index/index.md    # 读取文件
    python tools/ks.py list knowledge/permanent/concepts/  # 列出目录

    # 四步流程
    python tools/ks.py ingest --title "标题" --content "正文"
    python tools/ks.py digest --raw raw/2026/04/xxx.md
    python tools/ks.py output --question "你的问题"
    python tools/ks.py inspect

    # 文件操作
    python tools/ks.py create --file "path.md" --content "# 内容"
    python tools/ks.py append --file "path.md" --content "追加内容"
    python tools/ks.py stats                            # 知识库统计

    # 模式控制
    python tools/ks.py --local search "关键词"          # 强制本地模式
    python tools/ks.py --api health                    # 强制 API 模式

环境变量：
    OBSIDIAN_API_KEY       Obsidian Local REST API 的密钥
    OBSIDIAN_API_BASE      API 地址（默认自动探测）
    OBSIDIAN_VAULT_PATH    知识系统在 vault 中的路径
    KS_VAULT_PATH          本地模式下的知识库绝对路径
"""

import argparse
import json
import os
import sys
from datetime import date

# 将 tools 目录加入路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from obsidian_client import ObsidianClient
from local_client import LocalClient


# ==================== 客户端工厂 ====================

def create_client(force_mode: str = "auto", vault_path: str = ""):
    """
    创建知识系统客户端，支持自动模式切换。

    Args:
        force_mode: "auto" | "api" | "local"
        vault_path: 本地模式下的知识库路径

    Returns:
        (client, mode) 元组，client 为 ObsidianClient 或 LocalClient，
        mode 为 "api" 或 "local"
    """
    if force_mode == "local":
        client = LocalClient(vault_path=vault_path)
        return client, "local"

    if force_mode == "api":
        client = ObsidianClient()
        return client, "api"

    # 自动模式：先尝试 API，不可用则回退到本地
    client = ObsidianClient()
    if client.is_available():
        return client, "api"

    print("⚠️  Obsidian REST API 不可用，自动切换到本地文件模式")
    local_vault = vault_path or os.environ.get("KS_VAULT_PATH", "")
    local_client = LocalClient(vault_path=local_vault)
    return local_client, "local"


# ==================== 命令处理函数 ====================

def cmd_status(args: argparse.Namespace) -> None:
    """
    显示客户端连接状态。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    print(f"📡 当前模式: {'REST API' if mode == 'api' else '本地文件'}")
    status = client.status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


def cmd_health(args: argparse.Namespace) -> None:
    """
    执行健康检查。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    try:
        result = client.health_check()
        print("✅ 健康检查通过")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ConnectionError as e:
        print(f"❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        sys.exit(1)


def cmd_search(args: argparse.Namespace) -> None:
    """
    搜索知识系统中的笔记。

    Args:
        args: 命令行参数，包含 query 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    results = client.quick_search(args.query)
    if results:
        print(f"🔍 找到 {len(results)} 个匹配结果：\n")
        for r in results:
            print(f"  📄 {r}")
    else:
        print(f"🔍 未找到与「{args.query}」匹配的结果")


def cmd_read(args: argparse.Namespace) -> None:
    """
    读取指定文件的内容。

    Args:
        args: 命令行参数，包含 file 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    try:
        result = client.read_note(args.file)
        content = result.get("content", "")
        print(content)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {args.file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    """
    列出指定目录下的文件。

    Args:
        args: 命令行参数，包含 dir 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    try:
        result = client.list_dir(args.dir or "")
        files = result.get("files", {})
        if files:
            print(f"📁 {args.dir or '/'} 下的文件：\n")
            for name, info in files.items():
                file_type = "📂" if info.get("isDirectory") else "📄"
                print(f"  {file_type} {name}")
        else:
            print(f"📁 {args.dir or '/'} 为空")
    except Exception as e:
        print(f"❌ 列表失败: {e}")
        sys.exit(1)


def cmd_ingest(args: argparse.Namespace) -> None:
    """
    执行摄取步骤：创建标准化的 raw 文件。

    Args:
        args: 命令行参数，包含 title, content, source_url 等属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    content = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()

    tags = args.tags.split(",") if args.tags else None

    try:
        result = client.ingest_raw(
            title=args.title,
            content=content,
            source_type=args.source_type or "article",
            source_url=args.source_url or "",
            author=args.author or "",
            tags=tags,
        )
        print(f"📥 摄取成功: {args.title}")
        if isinstance(result, dict) and result.get("path"):
            print(f"   文件路径: {result['path']}")
    except Exception as e:
        print(f"❌ 摄取失败: {e}")
        sys.exit(1)


def cmd_create(args: argparse.Namespace) -> None:
    """
    创建或覆盖一个笔记文件。

    Args:
        args: 命令行参数，包含 file, content 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    content = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()

    try:
        result = client.create_note(args.file, content, overwrite=True)
        print(f"✅ 文件已创建: {args.file}")
        if isinstance(result, dict) and result.get("path"):
            print(f"   文件路径: {result['path']}")
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        sys.exit(1)


def cmd_append(args: argparse.Namespace) -> None:
    """
    向笔记文件末尾追加内容。

    Args:
        args: 命令行参数，包含 file, content 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    content = args.content
    if args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()

    try:
        result = client.append_to_note(args.file, content)
        print(f"✅ 内容已追加到: {args.file}")
    except Exception as e:
        print(f"❌ 追加失败: {e}")
        sys.exit(1)


def cmd_graph(args: argparse.Namespace) -> None:
    """
    在 Obsidian 中打开知识图谱视图。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    if mode == "local":
        print("⚠️  本地模式下无法打开知识图谱，请使用 --api 模式")
        sys.exit(1)
    try:
        client.open_knowledge_graph()
        print("🕸️ 已打开知识图谱视图")
    except Exception as e:
        print(f"❌ 打开图谱失败: {e}")
        sys.exit(1)


def cmd_open(args: argparse.Namespace) -> None:
    """
    在 Obsidian 中打开指定文件。

    Args:
        args: 命令行参数，包含 file 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    if mode == "local":
        result = client.open_in_obsidian(args.file)
        print(f"⚠️  {result.get('hint', '本地模式下无法在 Obsidian 中打开文件')}")
        print(f"   文件路径: {result.get('file_path', '')}")
        sys.exit(1)
    try:
        client.open_in_obsidian(args.file)
        print(f"📂 已在 Obsidian 中打开: {args.file}")
    except Exception as e:
        print(f"❌ 打开失败: {e}")
        sys.exit(1)


def cmd_index(args: argparse.Namespace) -> None:
    """
    读取并显示知识系统的总索引。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    try:
        content = client.read_knowledge_index()
        print("📋 知识系统总索引：\n")
        print(content)
    except Exception as e:
        print(f"❌ 读取索引失败: {e}")
        sys.exit(1)


def cmd_stats(args: argparse.Namespace) -> None:
    """
    显示知识库统计信息。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)
    if mode == "local" and hasattr(client, "get_stats"):
        stats = client.get_stats()
        print("📊 知识库统计：\n")
        print(f"  原始材料 (raw):     {stats.get('raw', 0)} 篇")
        print(f"  阅读摘要 (literature): {stats.get('literature', 0)} 篇")
        print(f"  概念卡 (concepts):   {stats.get('concepts', 0)} 张")
        print(f"  主题页 (topics):     {stats.get('topics', 0)} 个")
        print(f"  问答输出 (qa):       {stats.get('outputs_qa', 0)} 篇")
        print(f"  图文长文 (article):  {stats.get('outputs_article', 0)} 篇")
        print(f"  巡检报告 (inspection): {stats.get('inspection', 0)} 份")
        print(f"  ─────────────────")
        print(f"  总计:               {stats.get('total', 0)} 个文件")
    else:
        # API 模式下通过列出目录来统计
        try:
            dirs = {
                "raw": "raw",
                "literature": "knowledge/literature",
                "concepts": "knowledge/permanent/concepts",
                "topics": "knowledge/permanent/topics",
                "qa": "outputs/qa",
                "article": "outputs/article",
                "inspection": "inspection",
            }
            print("📊 知识库统计：\n")
            total = 0
            for label, dirpath in dirs.items():
                result = client.list_dir(dirpath)
                files = result.get("files", {})
                md_count = sum(1 for v in files.values() if not v.get("isDirectory"))
                total += md_count
                print(f"  {label:20s} {md_count} 个文件")
            print(f"  {'─' * 30}")
            print(f"  {'总计':20s} {total} 个文件")
        except Exception as e:
            print(f"❌ 统计失败: {e}")


def cmd_digest(args: argparse.Namespace) -> None:
    """
    执行消化步骤：读取 raw 文件，输出消化指引。

    注意：消化步骤的核心是 AI 处理，CLI 只负责准备材料和输出指引。
    实际消化应由 AI Agent 执行。

    Args:
        args: 命令行参数，包含 raw 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)

    # 读取指定的 raw 文件
    try:
        result = client.read_note(args.raw)
        raw_content = result.get("content", "")
    except FileNotFoundError:
        print(f"❌ Raw 文件不存在: {args.raw}")
        sys.exit(1)

    # 读取知识索引
    try:
        index_content = client.read_knowledge_index()
    except Exception:
        index_content = "（索引文件读取失败）"

    # 读取消化提示词
    try:
        prompt_result = client.read_note("prompts/digest.md")
        digest_prompt = prompt_result.get("content", "")
    except Exception:
        digest_prompt = "（提示词文件读取失败，请手动参考 prompts/digest.md）"

    print("=" * 60)
    print("📋 消化步骤准备完成")
    print("=" * 60)
    print(f"\n📄 Raw 文件: {args.raw}")
    print(f"📡 当前模式: {'REST API' if mode == 'api' else '本地文件'}")
    print(f"\n{'─' * 60}")
    print("请将以下内容发送给 AI Agent 执行消化：")
    print(f"{'─' * 60}\n")
    print(f"【消化提示词】\n{digest_prompt}\n")
    print(f"【知识索引】\n{index_content}\n")
    print(f"【Raw 文件内容】\n{raw_content[:2000]}...")
    print(f"\n{'─' * 60}")
    print("💡 消化完成后，使用以下命令创建产物：")
    print(f"   python tools/ks.py create --file \"knowledge/literature/xxx-summary.md\" --content \"...\"")
    print(f"   python tools/ks.py create --file \"knowledge/permanent/concepts/concept-xxx.md\" --content \"...\"")


def cmd_output(args: argparse.Namespace) -> None:
    """
    执行输出步骤：准备知识系统上下文，输出问答指引。

    Args:
        args: 命令行参数，包含 question 属性
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)

    # 读取知识索引
    try:
        index_content = client.read_knowledge_index()
    except Exception:
        index_content = "（索引文件读取失败）"

    # 读取输出提示词
    try:
        prompt_result = client.read_note("prompts/output.md")
        output_prompt = prompt_result.get("content", "")
    except Exception:
        output_prompt = "（提示词文件读取失败，请手动参考 prompts/output.md）"

    # 搜索相关问题
    keywords = args.question[:50]
    search_results = client.quick_search(keywords)

    print("=" * 60)
    print("📤 输出步骤准备完成")
    print("=" * 60)
    print(f"\n❓ 问题: {args.question}")
    print(f"📡 当前模式: {'REST API' if mode == 'api' else '本地文件'}")

    if search_results:
        print(f"\n🔍 相关文件 ({len(search_results)} 个)：")
        for r in search_results[:10]:
            print(f"   📄 {r}")

    print(f"\n{'─' * 60}")
    print("请将以下内容发送给 AI Agent 生成回答：")
    print(f"{'─' * 60}\n")
    print(f"【输出提示词】\n{output_prompt}\n")
    print(f"【知识索引】\n{index_content}\n")
    print(f"💡 生成回答后，使用以下命令保存到 outputs/qa/：")
    today = date.today().strftime("%Y-%m-%d")
    slug = args.question[:30].replace(" ", "-").lower()
    print(f"   python tools/ks.py create --file \"outputs/qa/{today}-qa-{slug}.md\" --content \"...\"")


def cmd_inspect(args: argparse.Namespace) -> None:
    """
    执行巡检步骤：检查知识系统结构性问题。

    Args:
        args: 命令行参数
    """
    client, mode = create_client(force_mode=args.mode, vault_path=args.vault)

    print("=" * 60)
    print("🔍 知识系统巡检")
    print("=" * 60)
    print(f"📡 当前模式: {'REST API' if mode == 'api' else '本地文件'}\n")

    # 1. 健康检查
    print("── 1. 目录结构检查 ──")
    health = client.health_check()
    if isinstance(health, dict):
        if health.get("status") == "ok":
            print("  ✅ 目录结构完整")
        else:
            missing = health.get("missing_dirs", [])
            print(f"  ⚠️  缺失目录: {', '.join(missing)}")
            for d in missing:
                os.makedirs(d, exist_ok=True)
                print(f"     📁 已创建: {d}")

    # 2. 断链检查（仅本地模式）
    if mode == "local" and hasattr(client, "find_broken_links"):
        print("\n── 2. 断链检查 ──")
        broken = client.find_broken_links()
        if broken:
            print(f"  ⚠️  发现 {len(broken)} 个断链：")
            for src, link in broken[:20]:
                print(f"     🔗 [{src}] → [[{link}]]")
        else:
            print("  ✅ 未发现断链")

    # 3. 统计信息
    print("\n── 3. 知识库统计 ──")
    if mode == "local" and hasattr(client, "get_stats"):
        stats = client.get_stats()
        for key, val in stats.items():
            if key != "total":
                print(f"  {key}: {val}")
        print(f"  总计: {stats.get('total', 0)} 个文件")
    else:
        print("  （API 模式下请使用 stats 命令查看统计）")

    # 4. 生成巡检报告
    today = date.today().strftime("%Y-%m-%d")
    report_file = f"inspection/{today}-auto-inspection.md"

    report_content = f"""---
id: inspection-{today}-auto
title: "自动巡检报告"
type: inspection
created_at: {today}
scope: [自动巡检]
mode: {mode}
---

## Summary

自动巡检报告，由 ks.py inspect 命令生成。

## Findings

### High Priority
（待 AI Agent 深度分析后补充）

### Medium Priority
（待 AI Agent 深度分析后补充）

### Low Priority
（待 AI Agent 深度分析后补充）

## Statistics

- 巡检模式：{mode}
- 巡检时间：{today}

## Suggested Fixes

（待 AI Agent 深度分析后补充）
"""

    try:
        client.create_note(report_file, report_content, overwrite=True)
        print(f"\n📋 巡检报告已生成: {report_file}")
        print("💡 请让 AI Agent 对知识系统进行深度巡检，补充报告内容。")
    except Exception as e:
        print(f"\n⚠️  巡检报告生成失败: {e}")


# ==================== 主入口 ====================

def main():
    """
    主入口：解析命令行参数并执行对应命令。

    支持全局参数：
        --local    强制使用本地文件模式
        --api      强制使用 REST API 模式
        --vault    指定知识库路径（本地模式）
    """
    parser = argparse.ArgumentParser(
        description="知识系统 CLI — TRAE 操作入口（双模式版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模式控制：
  python tools/ks.py status                  # 自动检测模式
  python tools/ks.py --local status           # 强制本地模式
  python tools/ks.py --api health             # 强制 API 模式

基础操作：
  python tools/ks.py search "关键词"
  python tools/ks.py read knowledge/index/index.md
  python tools/ks.py list knowledge/permanent/concepts/
  python tools/ks.py stats

四步流程：
  python tools/ks.py ingest --title "标题" --content "正文"
  python tools/ks.py digest --raw raw/2026/04/xxx.md
  python tools/ks.py output --question "你的问题"
  python tools/ks.py inspect

文件操作：
  python tools/ks.py create --file "path.md" --content "# 内容"
  python tools/ks.py append --file "path.md" --content "追加内容"
        """,
    )

    # 全局参数
    parser.add_argument("--local", action="store_true", help="强制使用本地文件模式")
    parser.add_argument("--api", action="store_true", help="强制使用 REST API 模式")
    parser.add_argument("--vault", default="", help="指定知识库路径（本地模式）")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # status
    subparsers.add_parser("status", help="查看连接状态")

    # health
    subparsers.add_parser("health", help="健康检查")

    # search
    search_parser = subparsers.add_parser("search", help="搜索知识系统中的笔记")
    search_parser.add_argument("query", help="搜索关键词")

    # read
    read_parser = subparsers.add_parser("read", help="读取文件内容")
    read_parser.add_argument("file", help="文件路径")

    # list
    list_parser = subparsers.add_parser("list", help="列出目录下的文件")
    list_parser.add_argument("dir", nargs="?", default="", help="目录路径")

    # ingest
    ingest_parser = subparsers.add_parser("ingest", help="摄取资料为 raw 文件")
    ingest_parser.add_argument("--title", required=True, help="资料标题")
    ingest_parser.add_argument("--content", default="", help="正文内容")
    ingest_parser.add_argument("--content-file", default="", help="从文件读取正文内容")
    ingest_parser.add_argument("--source-url", default="", help="来源链接")
    ingest_parser.add_argument("--author", default="", help="作者")
    ingest_parser.add_argument("--source-type", default="article", help="来源类型")
    ingest_parser.add_argument("--tags", default="", help="标签（逗号分隔）")

    # digest
    digest_parser = subparsers.add_parser("digest", help="消化 raw 文件（准备材料）")
    digest_parser.add_argument("--raw", required=True, help="要消化的 raw 文件路径")

    # output
    output_parser = subparsers.add_parser("output", help="基于知识系统回答问题")
    output_parser.add_argument("--question", required=True, help="你的问题")

    # inspect
    subparsers.add_parser("inspect", help="执行知识系统巡检")

    # create
    create_parser = subparsers.add_parser("create", help="创建或覆盖笔记文件")
    create_parser.add_argument("--file", required=True, help="文件路径")
    create_parser.add_argument("--content", default="", help="文件内容")
    create_parser.add_argument("--content-file", default="", help="从文件读取内容")

    # append
    append_parser = subparsers.add_parser("append", help="向笔记追加内容")
    append_parser.add_argument("--file", required=True, help="文件路径")
    append_parser.add_argument("--content", default="", help="追加内容")
    append_parser.add_argument("--content-file", default="", help="从文件读取内容")

    # open
    open_parser = subparsers.add_parser("open", help="在 Obsidian 中打开文件")
    open_parser.add_argument("file", help="文件路径")

    # graph
    subparsers.add_parser("graph", help="在 Obsidian 中打开知识图谱")

    # index
    subparsers.add_parser("index", help="查看知识系统总索引")

    # stats
    subparsers.add_parser("stats", help="查看知识库统计信息")

    args = parser.parse_args()

    # 确定模式
    if args.api:
        args.mode = "api"
    elif args.local:
        args.mode = "local"
    else:
        args.mode = "auto"

    if not args.command:
        parser.print_help()
        return

    # 命令路由
    commands = {
        "status": cmd_status,
        "health": cmd_health,
        "search": cmd_search,
        "read": cmd_read,
        "list": cmd_list,
        "ingest": cmd_ingest,
        "digest": cmd_digest,
        "output": cmd_output,
        "inspect": cmd_inspect,
        "create": cmd_create,
        "append": cmd_append,
        "open": cmd_open,
        "graph": cmd_graph,
        "index": cmd_index,
        "stats": cmd_stats,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

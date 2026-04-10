"""
知识系统本地文件操作客户端。

当 Obsidian REST API 不可用时，提供纯文件系统操作作为后备方案。
接口设计与 ObsidianClient 保持一致，便于 ks.py 统一调用。

特性：
    - 直接读写文件系统，无需 Obsidian 运行
    - 支持全文搜索（基于 grep/ripgrep）
    - 自动创建缺失的目录结构
    - 接口兼容 ObsidianClient，可无缝切换

使用场景：
    - Obsidian 未运行时
    - VM 无法访问宿主机网络时
    - 自动化批量操作时
"""

import fnmatch
import logging
import os
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Optional

# 模块级日志
logger = logging.getLogger(__name__)


class LocalClient:
    """
    知识系统本地文件操作客户端。

    直接操作文件系统，接口与 ObsidianClient 兼容。
    """

    def __init__(self, vault_path: str = ""):
        """
        初始化本地客户端。

        Args:
            vault_path: 知识库根目录的绝对路径。
                        为空时自动检测（向上查找包含 .obsidian/ 的目录）。
        """
        if vault_path:
            self.vault_path = Path(vault_path).resolve()
        else:
            self.vault_path = self._detect_vault_path()

        if not self.vault_path.exists():
            raise FileNotFoundError(f"知识库目录不存在: {self.vault_path}")

        logger.info(f"本地客户端初始化，知识库路径: {self.vault_path}")

    def _detect_vault_path(self) -> Path:
        """
        自动检测知识库根目录（查找包含 .obsidian/ 的目录）。

        Returns:
            知识库根目录的 Path 对象

        Raises:
            FileNotFoundError: 未找到知识库目录
        """
        # 从当前工作目录向上查找
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / ".obsidian").is_dir():
                logger.info(f"自动检测到知识库目录: {parent}")
                return parent

        # 尝试常见路径
        common_paths = [
            Path.home() / "knowledge-system",
            Path.home() / "Documents" / "knowledge-system",
            Path.home() / "Desktop" / "knowledge-system",
        ]
        for p in common_paths:
            if (p / ".obsidian").is_dir():
                logger.info(f"在常见路径找到知识库: {p}")
                return p

        raise FileNotFoundError(
            "未找到知识库目录。请通过 --vault 参数指定路径，"
            "或确保当前目录（或其父目录）包含 .obsidian/ 文件夹。"
        )

    def _resolve(self, filename: str) -> Path:
        """
        将相对文件名解析为绝对路径。

        Args:
            filename: 相对于知识库根目录的文件路径

        Returns:
            解析后的绝对路径
        """
        return (self.vault_path / filename).resolve()

    # ==================== 兼容性方法（与 ObsidianClient 接口一致） ====================

    def is_available(self) -> bool:
        """
        检查本地客户端是否可用（始终返回 True）。

        Returns:
            True
        """
        return True

    def status(self) -> dict:
        """
        获取客户端状态摘要。

        Returns:
            包含 available, vault_path 的状态字典
        """
        return {
            "available": True,
            "mode": "local",
            "vault_path": str(self.vault_path),
        }

    def health_check(self) -> dict:
        """
        执行健康检查，验证知识库目录结构完整性。

        Returns:
            包含状态和统计信息的字典
        """
        required_dirs = [
            "raw", "knowledge", "knowledge/literature",
            "knowledge/permanent", "knowledge/permanent/concepts",
            "knowledge/permanent/topics", "knowledge/index",
            "knowledge/fleeting", "outputs", "inspection",
            "prompts", "schemas",
        ]
        missing = []
        for d in required_dirs:
            if not (self.vault_path / d).is_dir():
                missing.append(d)

        return {
            "status": "ok" if not missing else "incomplete",
            "vault_path": str(self.vault_path),
            "missing_dirs": missing,
            "note_count": self._count_md_files(),
        }

    def _count_md_files(self) -> int:
        """统计知识库中的 Markdown 文件数量。"""
        try:
            result = subprocess.run(
                ["find", str(self.vault_path), "-name", "*.md", "-type", "f"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
        except Exception:
            pass
        return 0

    # ==================== 笔记 CRUD ====================

    def create_note(
        self,
        filename: str,
        content: str,
        overwrite: bool = False,
    ) -> dict:
        """
        创建或覆盖一个笔记文件。

        Args:
            filename: 文件名（相对于知识库根目录）
            content: 笔记的完整内容（Markdown 格式）
            overwrite: 是否覆盖已有文件

        Returns:
            包含操作结果的字典
        """
        filepath = self._resolve(filename)

        if filepath.exists() and not overwrite:
            return {"success": False, "error": f"文件已存在: {filename}"}

        # 自动创建父目录
        filepath.parent.mkdir(parents=True, exist_ok=True)

        filepath.write_text(content, encoding="utf-8")
        logger.info(f"✅ 文件已创建: {filename}")
        return {"success": True, "path": str(filepath)}

    def read_note(self, filename: str) -> dict:
        """
        读取一个笔记文件的内容。

        Args:
            filename: 文件名（相对于知识库根目录）

        Returns:
            包含笔记内容的字典

        Raises:
            FileNotFoundError: 文件不存在
        """
        filepath = self._resolve(filename)
        if not filepath.exists():
            raise FileNotFoundError(f"文件不存在: {filename}")

        content = filepath.read_text(encoding="utf-8")
        return {"content": content, "path": str(filepath)}

    def update_note(self, filename: str, content: str) -> dict:
        """
        更新（覆盖）一个已有笔记文件。

        Args:
            filename: 文件名
            content: 新的完整内容

        Returns:
            操作结果字典
        """
        return self.create_note(filename, content, overwrite=True)

    def append_to_note(self, filename: str, content: str) -> dict:
        """
        向笔记文件末尾追加内容。

        Args:
            filename: 文件名
            content: 要追加的内容

        Returns:
            操作结果字典
        """
        filepath = self._resolve(filename)
        if not filepath.exists():
            return {"success": False, "error": f"文件不存在: {filename}"}

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"✅ 内容已追加到: {filename}")
        return {"success": True, "path": str(filepath)}

    def insert_at_heading(
        self,
        filename: str,
        heading: str,
        content: str,
        insert_after: bool = True,
        create: bool = True,
    ) -> dict:
        """
        在笔记的指定标题处插入内容。

        Args:
            filename: 文件名
            heading: 目标标题（如 "## Key Points"）
            content: 要插入的内容
            insert_after: True 在标题后插入
            create: 如果标题不存在是否创建

        Returns:
            操作结果字典
        """
        filepath = self._resolve(filename)
        if not filepath.exists():
            return {"success": False, "error": f"文件不存在: {filename}"}

        text = filepath.read_text(encoding="utf-8")
        lines = text.split("\n")

        # 查找标题位置
        heading_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(heading.lstrip("#").strip()):
                # 匹配标题内容（忽略 # 数量差异）
                heading_idx = i
                break
            elif line.strip() == heading.strip():
                heading_idx = i
                break

        if heading_idx == -1:
            if create:
                # 在文件末尾添加标题和内容
                new_text = text + f"\n\n{heading}\n\n{content}"
                filepath.write_text(new_text, encoding="utf-8")
                return {"success": True, "action": "created_heading"}
            return {"success": False, "error": f"未找到标题: {heading}"}

        # 在标题后插入
        insert_idx = heading_idx + 1 if insert_after else heading_idx
        lines.insert(insert_idx, f"\n{content}")
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return {"success": True, "action": "inserted"}

    def delete_note(self, filename: str) -> dict:
        """
        删除一个笔记文件。

        Args:
            filename: 文件名

        Returns:
            操作结果字典
        """
        filepath = self._resolve(filename)
        if not filepath.exists():
            return {"success": False, "error": f"文件不存在: {filename}"}

        filepath.unlink()
        logger.info(f"🗑️ 文件已删除: {filename}")
        return {"success": True}

    # ==================== 文件列表 ====================

    def list_dir(self, dirpath: str = "") -> dict:
        """
        列出指定目录下的文件。

        Args:
            dirpath: 目录路径，空字符串表示知识库根目录

        Returns:
            包含文件列表的字典
        """
        target = self._resolve(dirpath) if dirpath else self.vault_path
        if not target.exists():
            return {"files": {}, "error": f"目录不存在: {dirpath}"}

        files = {}
        for item in sorted(target.iterdir()):
            files[item.name] = {
                "isDirectory": item.is_dir(),
                "name": item.name,
            }

        return {"files": files}

    # ==================== 搜索 ====================

    def search(self, query: str, context_length: int = 100) -> dict:
        """
        搜索笔记内容（使用 grep）。

        Args:
            query: 搜索关键词
            context_length: 返回的上下文长度（字符数）

        Returns:
            包含搜索结果的字典
        """
        try:
            result = subprocess.run(
                [
                    "grep", "-rn", "--include=*.md",
                    "-C", "1", query, str(self.vault_path)
                ],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                matches = []
                for line in result.stdout.strip().split("\n"):
                    # 解析 grep 输出格式: filepath:linenum:content
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        rel_path = os.path.relpath(parts[0], str(self.vault_path))
                        matches.append({
                            "filename": rel_path,
                            "line": int(parts[1]),
                            "context": parts[2][:context_length],
                        })
                return {"results": matches}
            return {"results": []}
        except Exception as e:
            return {"results": [], "error": str(e)}

    def search_simple(self, query: str) -> dict:
        """
        简单搜索（返回匹配的文件列表）。

        Args:
            query: 搜索关键词

        Returns:
            包含匹配文件列表的字典
        """
        try:
            result = subprocess.run(
                [
                    "grep", "-rl", "--include=*.md",
                    query, str(self.vault_path)
                ],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                files = []
                for f in result.stdout.strip().split("\n"):
                    rel = os.path.relpath(f, str(self.vault_path))
                    files.append(rel)
                return {"results": files}
            return {"results": []}
        except Exception as e:
            return {"results": [], "error": str(e)}

    # ==================== 知识系统专用方法 ====================

    def ingest_raw(
        self,
        title: str,
        content: str,
        source_type: str = "article",
        source_url: str = "",
        author: str = "",
        tags: Optional[list] = None,
    ) -> dict:
        """
        执行摄取步骤：创建标准化的 raw 文件。

        Args:
            title: 资料标题
            content: 清洗后的正文内容
            source_type: 来源类型
            source_url: 来源链接
            author: 作者
            tags: 标签列表

        Returns:
            操作结果字典
        """
        today = date.today().strftime("%Y-%m-%d")
        slug = title.lower().replace(" ", "-")[:50]

        # 检查当天已有文件数，自动递增序号
        raw_dir = self.vault_path / "raw" / today[:4] / today[5:7]
        seq = 1
        if raw_dir.exists():
            for f in raw_dir.iterdir():
                if f.name.startswith(f"{today}-{slug}-"):
                    try:
                        num = int(f.name.split("-")[-1].replace(".md", ""))
                        seq = max(seq, num + 1)
                    except ValueError:
                        pass

        filename = f"raw/{today[:4]}/{today[5:7]}/{today}-{slug}-{seq:03d}.md"

        frontmatter = f"""---
id: {today}-{slug}-{seq:03d}
title: "{title}"
source_type: {source_type}
source_url: "{source_url}"
author: "{author}"
published_at: {today}
captured_at: {today}
content_type: article
status: complete
tags:
"""

        if tags:
            for tag in tags:
                frontmatter += f"  - {tag}\n"

        frontmatter += """attachments: []
---

## Raw Content

"""
        full_content = (
            frontmatter + content
            + "\n\n## Capture Notes\n\n- 完整性说明：\n- 来源类型：正文\n- 缺失说明：\n"
        )

        return self.create_note(filename, full_content, overwrite=True)

    def quick_search(self, query: str) -> list:
        """
        快速搜索知识系统中的笔记，返回匹配的文件路径列表。

        Args:
            query: 搜索关键词

        Returns:
            匹配的文件路径列表
        """
        result = self.search_simple(query)
        if isinstance(result, dict):
            return result.get("results", [])
        return []

    def read_knowledge_index(self) -> str:
        """
        读取知识系统的总索引文件。

        Returns:
            索引文件的内容字符串
        """
        result = self.read_note("knowledge/index/index.md")
        return result.get("content", "")

    def open_in_obsidian(self, filename: str) -> dict:
        """
        本地模式下无法在 Obsidian 中打开文件。

        Args:
            filename: 文件名

        Returns:
            提示信息字典
        """
        return {
            "success": False,
            "hint": "本地模式下无法在 Obsidian 中打开文件。"
                   "请使用 REST API 模式（确保 Obsidian 正在运行）。",
            "file_path": str(self._resolve(filename)),
        }

    def open_knowledge_graph(self) -> dict:
        """
        本地模式下无法打开知识图谱。

        Returns:
            提示信息字典
        """
        return {
            "success": False,
            "hint": "本地模式下无法打开知识图谱。请使用 REST API 模式。",
        }

    def open_backlinks(self) -> dict:
        """
        本地模式下无法打开反向链接面板。

        Returns:
            提示信息字典
        """
        return {
            "success": False,
            "hint": "本地模式下无法打开反向链接面板。请使用 REST API 模式。",
        }

    # ==================== 本地模式特有方法 ====================

    def get_stats(self) -> dict:
        """
        获取知识库统计信息。

        Returns:
            包含各目录文件数量的统计字典
        """
        stats = {}
        dirs = {
            "raw": "raw",
            "literature": "knowledge/literature",
            "concepts": "knowledge/permanent/concepts",
            "topics": "knowledge/permanent/topics",
            "outputs_qa": "outputs/qa",
            "outputs_article": "outputs/article",
            "inspection": "inspection",
        }
        for key, dirpath in dirs.items():
            target = self.vault_path / dirpath
            if target.exists():
                count = len(list(target.glob("*.md")))
                stats[key] = count
            else:
                stats[key] = 0

        stats["total"] = sum(stats.values())
        return stats

    def find_broken_links(self) -> list:
        """
        查找知识库中断裂的 wikilink。

        Returns:
            包含断链信息的列表，每项为 (源文件, 断裂链接) 元组
        """
        broken = []
        pattern = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')

        for md_file in self.vault_path.rglob("*.md"):
            # 跳过 .obsidian 目录
            if ".obsidian" in str(md_file):
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            for match in pattern.finditer(content):
                link_target = match.group(1)
                # 尝试找到对应的文件
                possible_names = [
                    f"{link_target}.md",
                    f"{link_target}.canvas",
                ]
                found = False
                for name in possible_names:
                    if (self.vault_path / name).exists():
                        found = True
                        break
                    # 递归搜索
                    for f in self.vault_path.rglob(name):
                        found = True
                        break
                    if found:
                        break

                if not found:
                    rel_path = os.path.relpath(str(md_file), str(self.vault_path))
                    broken.append((rel_path, link_target))

        return broken

"""
知识系统 Obsidian REST API 客户端模块（升级版）。

提供通过 Obsidian Local REST API 插件与 Obsidian 深度交互的能力，
包括创建/读取/更新/删除笔记、搜索、打开文件、执行命令等。

升级特性：
    - 自动探测：自动尝试多个可能的宿主机 IP 和端口
    - 健康检查：is_available() 方法快速判断 API 是否可达
    - 重试机制：网络请求失败时自动重试
    - 连接缓存：探测结果缓存，避免重复探测

依赖：
    pip install requests

使用前需要：
    1. 在 Obsidian 中安装并启用 Local REST API 插件
    2. 在插件设置中生成 API Key
    3. 配置本模块的 API_BASE 和 API_KEY
"""

import json
import logging
import os
import socket
import subprocess
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 模块级日志
logger = logging.getLogger(__name__)

# 默认探测的候选地址列表
_DEFAULT_PROBE_ADDRESSES = [
    "https://127.0.0.1:27124",
    "https://host.docker.internal:27124",
    "https://192.168.64.1:27124",
    "https://172.17.0.1:27124",
    "https://192.168.65.2:27124",
    "https://10.0.2.2:27124",
]

# 从插件 data.json 中读取的默认 API Key
_DEFAULT_API_KEY = "YOUR KEY"


class ObsidianClient:
    """
    Obsidian Local REST API 客户端，封装所有与 Obsidian 交互的方法。

    支持自动探测宿主机地址、健康检查、请求重试等特性。
    """

    def __init__(
        self,
        api_base: str = "",
        api_key: Optional[str] = None,
        vault_path: Optional[str] = None,
        auto_probe: bool = True,
        timeout: int = 5,
    ):
        """
        初始化 Obsidian 客户端。

        Args:
            api_base: Obsidian Local REST API 地址。
                      为空时自动探测（默认行为）。
            api_key: API 密钥，优先级：参数 > 环境变量 > 默认值
            vault_path: 知识库在 Obsidian vault 中的相对路径
            auto_probe: 是否在首次请求时自动探测可用地址
            timeout: 请求超时时间（秒）
        """
        self.api_key = api_key or os.environ.get("OBSIDIAN_API_KEY", _DEFAULT_API_KEY)
        self.vault_path = vault_path or os.environ.get("OBSIDIAN_VAULT_PATH", "")
        self.timeout = timeout
        self._auto_probe = auto_probe

        # 连接状态
        self._api_base = api_base.rstrip("/") if api_base else ""
        self._available = None  # None = 未探测, True/False = 已知状态
        self._session = None

        # 构建 HTTP session（带重试）
        self._build_session()

    def _build_session(self) -> None:
        """构建带重试策略的 HTTP session。"""
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        # 禁用 SSL 证书验证（插件使用自签名证书）
        self._session.verify = False
        # 抑制 InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # 配置重试策略
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)

    # ==================== 自动探测 ====================

    def _detect_gateway_ip(self) -> list:
        """
        检测 VM 的默认网关 IP，作为候选的宿主机地址。

        Returns:
            包含候选 IP 地址的列表
        """
        candidates = []
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    parts = line.split()
                    if "via" in parts:
                        idx = parts.index("via")
                        if idx + 1 < len(parts):
                            ip = parts[idx + 1]
                            candidates.append(f"https://{ip}:27124")
        except Exception:
            pass
        return candidates

    def probe(self) -> Optional[str]:
        """
        探测可用的 Obsidian REST API 地址。

        按以下顺序尝试：
        1. 环境变量 OBSIDIAN_API_BASE 指定的地址
        2. 构造函数中指定的 api_base
        3. VM 默认网关地址
        4. 常见 Docker/VM 网关地址列表

        Returns:
            第一个可用的 API 地址，如果全部不可用则返回 None
        """
        logger.info("开始探测 Obsidian REST API 地址...")

        # 构建候选地址列表（去重，保持顺序）
        candidates = []
        seen = set()

        # 优先级 1：环境变量
        env_base = os.environ.get("OBSIDIAN_API_BASE", "")
        if env_base:
            env_base = env_base.rstrip("/")
            candidates.append(env_base)
            seen.add(urlparse(env_base).netloc)

        # 优先级 2：构造函数指定的地址
        if self._api_base:
            candidates.append(self._api_base)
            seen.add(urlparse(self._api_base).netloc)

        # 优先级 3：VM 默认网关
        for addr in self._detect_gateway_ip():
            netloc = urlparse(addr).netloc
            if netloc not in seen:
                candidates.append(addr)
                seen.add(netloc)

        # 优先级 4：预定义地址列表
        for addr in _DEFAULT_PROBE_ADDRESSES:
            netloc = urlparse(addr).netloc
            if netloc not in seen:
                candidates.append(addr)
                seen.add(netloc)

        # 逐个尝试
        for addr in candidates:
            try:
                logger.debug(f"尝试连接: {addr}")
                resp = requests.get(
                    f"{addr}/",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    verify=False,
                    timeout=3,
                )
                if resp.status_code == 200:
                    logger.info(f"✅ Obsidian REST API 可用: {addr}")
                    self._api_base = addr
                    self._available = True
                    return addr
            except (requests.ConnectionError, requests.Timeout):
                logger.debug(f"❌ 连接失败: {addr}")
                continue
            except Exception as e:
                logger.debug(f"❌ 异常: {addr} - {e}")
                continue

        logger.warning("⚠️ 未找到可用的 Obsidian REST API 地址")
        self._available = False
        return None

    def is_available(self) -> bool:
        """
        检查 Obsidian REST API 是否可用。

        首次调用会触发自动探测，后续调用使用缓存结果。
        可通过 reset_probe() 清除缓存强制重新探测。

        Returns:
            True 如果 API 可用，False 不可用
        """
        if self._available is not None:
            return self._available

        if self._auto_probe:
            return self.probe() is not None

        # 不自动探测时，直接尝试当前地址
        if self._api_base:
            try:
                resp = self._session.get(
                    self._url("/"),
                    timeout=self.timeout,
                )
                self._available = resp.status_code == 200
                return self._available
            except Exception:
                self._available = False
                return False

        self._available = False
        return False

    def reset_probe(self) -> None:
        """重置探测缓存，下次 is_available() 会重新探测。"""
        self._available = None
        logger.info("探测缓存已重置")

    def ensure_available(self) -> bool:
        """
        确保 API 可用，不可用时抛出明确的异常。

        Returns:
            True 如果可用

        Raises:
            ConnectionError: API 不可用
        """
        if not self.is_available():
            raise ConnectionError(
                "Obsidian REST API 不可用。请确认：\n"
                "  1. Obsidian 已打开并加载了知识库\n"
                "  2. Local REST API 插件已启用\n"
                "  3. API Key 已正确配置\n"
                "  4. 网络可达（VM → 宿主机）\n"
                "提示：可使用 --local 模式直接操作文件，无需 Obsidian 运行。"
            )
        return True

    # ==================== 内部工具方法 ====================

    def _full_path(self, filename: str) -> str:
        """
        拼接完整的 vault 内文件路径。

        Args:
            filename: 文件名或相对路径

        Returns:
            拼接后的完整路径
        """
        if self.vault_path:
            return f"{self.vault_path}/{filename}"
        return filename

    def _url(self, endpoint: str) -> str:
        """
        拼接完整的 API URL。

        Args:
            endpoint: API 端点路径

        Returns:
            完整的 URL
        """
        return f"{self.api_base}{endpoint}"

    # ==================== 状态检查 ====================

    def health_check(self) -> dict:
        """
        检查 Obsidian REST API 是否可用，返回详细状态。

        Returns:
            包含连接状态和 API 信息的字典

        Raises:
            ConnectionError: 无法连接到 Obsidian
        """
        self.ensure_available()
        resp = self._session.get(self._url("/"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def status(self) -> dict:
        """
        获取客户端连接状态摘要（不抛异常）。

        Returns:
            包含 available, api_base, vault_path 的状态字典
        """
        return {
            "available": self.is_available(),
            "api_base": self._api_base or "未配置",
            "vault_path": self.vault_path or "默认",
            "api_key_set": bool(self.api_key),
        }

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
            filename: 文件名（相对于 vault 根目录）
            content: 笔记的完整内容（Markdown 格式）
            overwrite: 是否覆盖已有文件

        Returns:
            API 返回的响应字典

        Raises:
            ConnectionError: API 不可用
            requests.HTTPError: 创建失败
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        if overwrite:
            resp = self._session.put(
                self._url(f"/vault/{full_path}"),
                data=content.encode("utf-8"),
                headers={"Content-Type": "text/markdown"},
                timeout=self.timeout,
            )
        else:
            resp = self._session.post(
                self._url(f"/vault/{full_path}"),
                data=content.encode("utf-8"),
                headers={"Content-Type": "text/markdown"},
                timeout=self.timeout,
            )
        resp.raise_for_status()
        return resp.json()

    def read_note(self, filename: str) -> dict:
        """
        读取一个笔记文件的内容。

        Args:
            filename: 文件名（相对于 vault 根目录）

        Returns:
            包含笔记内容的字典

        Raises:
            ConnectionError: API 不可用
            requests.HTTPError: 文件不存在或读取失败
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        resp = self._session.get(
            self._url(f"/vault/{full_path}"),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def update_note(self, filename: str, content: str) -> dict:
        """
        更新（覆盖）一个已有笔记文件。

        Args:
            filename: 文件名
            content: 新的完整内容

        Returns:
            API 返回的响应字典
        """
        return self.create_note(filename, content, overwrite=True)

    def append_to_note(self, filename: str, content: str) -> dict:
        """
        向笔记文件末尾追加内容。

        Args:
            filename: 文件名
            content: 要追加的内容

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        resp = self._session.post(
            self._url(f"/vault/{full_path}"),
            data=content.encode("utf-8"),
            headers={"Content-Type": "text/markdown"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

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
            API 返回的响应字典
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        body = {
            "heading": heading,
            "content": content,
            "insert_after": insert_after,
            "create": create,
        }
        resp = self._session.patch(
            self._url(f"/vault/{full_path}"),
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def delete_note(self, filename: str) -> dict:
        """
        删除一个笔记文件。

        Args:
            filename: 文件名

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        resp = self._session.delete(
            self._url(f"/vault/{full_path}"),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # ==================== 文件列表 ====================

    def list_dir(self, dirpath: str = "") -> dict:
        """
        列出指定目录下的文件。

        Args:
            dirpath: 目录路径，空字符串表示 vault 根目录

        Returns:
            包含文件列表的字典
        """
        self.ensure_available()
        if dirpath and self.vault_path:
            dirpath = f"{self.vault_path}/{dirpath}"
        elif self.vault_path:
            dirpath = self.vault_path

        url = f"/vault/{dirpath}/" if dirpath else "/vault/"
        resp = self._session.get(self._url(url), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    # ==================== 搜索 ====================

    def search(self, query: str, context_length: int = 100) -> dict:
        """
        搜索笔记内容。

        Args:
            query: 搜索关键词
            context_length: 返回的上下文长度

        Returns:
            包含搜索结果的字典
        """
        self.ensure_available()
        body = {"query": query, "contextLength": context_length}
        resp = self._session.post(
            self._url("/search/"),
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def search_simple(self, query: str) -> dict:
        """
        简单搜索（返回匹配的文件列表）。

        Args:
            query: 搜索关键词

        Returns:
            包含匹配文件列表的字典
        """
        self.ensure_available()
        body = {"query": query}
        resp = self._session.post(
            self._url("/search/simple/"),
            json=body,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # ==================== 打开文件 ====================

    def open_note(self, filename: str) -> dict:
        """
        在 Obsidian 中打开指定文件。

        Args:
            filename: 文件名

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        full_path = self._full_path(filename)
        resp = self._session.post(
            self._url(f"/open/{full_path}"),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # ==================== 当前活动文件 ====================

    def get_active_note(self) -> dict:
        """
        获取 Obsidian 中当前打开的文件内容。

        Returns:
            包含当前文件内容的字典
        """
        self.ensure_available()
        resp = self._session.get(self._url("/active/"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def update_active_note(self, content: str) -> dict:
        """
        更新 Obsidian 中当前打开的文件。

        Args:
            content: 新的完整内容

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        resp = self._session.put(
            self._url("/active/"),
            data=content.encode("utf-8"),
            headers={"Content-Type": "text/markdown"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def append_to_active_note(self, content: str) -> dict:
        """
        向当前打开的文件追加内容。

        Args:
            content: 要追加的内容

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        resp = self._session.post(
            self._url("/active/"),
            data=content.encode("utf-8"),
            headers={"Content-Type": "text/markdown"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # ==================== 命令执行 ====================

    def list_commands(self) -> dict:
        """
        获取 Obsidian 中所有可用的命令列表。

        Returns:
            包含命令列表的字典
        """
        self.ensure_available()
        resp = self._session.get(self._url("/commands/"), timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def execute_command(self, command_id: str) -> dict:
        """
        执行一个 Obsidian 命令。

        Args:
            command_id: 命令 ID（如 "graph:open"）

        Returns:
            API 返回的响应字典
        """
        self.ensure_available()
        resp = self._session.post(
            self._url(f"/commands/{command_id}/"),
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

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
        执行摄取步骤：创建标准化的 raw 文件并写入 Obsidian。

        Args:
            title: 资料标题
            content: 清洗后的正文内容
            source_type: 来源类型（x/article/pdf/podcast/note/conversation）
            source_url: 来源链接
            author: 作者
            tags: 标签列表

        Returns:
            API 返回的响应字典
        """
        from datetime import date

        today = date.today().strftime("%Y-%m-%d")
        slug = title.lower().replace(" ", "-")[:50]
        filename = f"raw/{today[:4]}/{today[5:7]}/{today}-{slug}-001.md"

        frontmatter = f"""---
id: {today}-{slug}-001
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
        在 Obsidian 中打开指定文件（便捷方法）。

        Args:
            filename: 文件名

        Returns:
            API 返回的响应字典
        """
        return self.open_note(filename)

    def open_knowledge_graph(self) -> dict:
        """
        在 Obsidian 中打开知识图谱视图。

        Returns:
            API 返回的响应字典
        """
        return self.execute_command("graph:open")

    def open_backlinks(self) -> dict:
        """
        在 Obsidian 中打开反向链接面板。

        Returns:
            API 返回的响应字典
        """
        return self.execute_command("backlink:open")

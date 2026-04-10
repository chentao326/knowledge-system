# Obsidian 集成配置指南

> 本指南说明如何配置 TRAE 与 Obsidian 的联动。系统支持**双模式运行**：
> - **REST API 模式**：通过 Obsidian Local REST API 深度交互（需 Obsidian 运行）
> - **Local 模式**：直接操作文件系统（无需 Obsidian，自动回退）
>
> 默认自动检测 Obsidian 可用性，智能切换模式。

---

## 架构概览

```
TRAE (AI Agent / SOLO)
    │
    ├── 自动检测 Obsidian REST API 是否可用
    │       │
    │       ├── ✅ 可用 → REST API 模式
    │       │   ├── 创建/读取/更新/删除笔记
    │       │   ├── 搜索笔记内容
    │       │   ├── 在 Obsidian 中打开文件
    │       │   ├── 打开知识图谱
    │       │   └── 执行 Obsidian 命令
    │       │
    │       └── ❌ 不可用 → Local 模式（自动回退）
    │           ├── 直接读写文件系统
    │           ├── grep 全文搜索
    │           ├── 断链检查
    │           └── 知识库统计
    │
    └── 统一 CLI 入口: python tools/ks.py [命令]
```

---

## 前置条件

- Obsidian 已安装（[下载地址](https://obsidian.md/)）
- 知识系统目录 `knowledge-system/` 已存在
- Python 3.8+ 和 `requests` 库

---

## 快速开始（无需配置）

如果你只是想快速使用，不需要 Obsidian 联动功能，直接运行即可：

```bash
cd knowledge-system
python tools/ks.py --local status     # 查看状态
python tools/ks.py --local stats      # 查看统计
python tools/ks.py --local search "关键词"  # 搜索
```

系统会自动检测到 `.obsidian/` 目录并使用本地文件模式。

---

## 配置 REST API 模式（可选，获得完整功能）

如果你希望在 TRAE 中直接操作 Obsidian（打开文件、查看图谱等），需要配置 REST API。

### 第一步：在 Obsidian 中打开知识库

1. 打开 Obsidian
2. 点击「打开文件夹为仓库」
3. 选择 `knowledge-system/` 的**父目录**（即包含 `knowledge-system/` 的那个文件夹）
4. 确认打开

> **注意**：如果你把 `knowledge-system/` 本身作为仓库打开，vault 路径就是根目录 `/`。如果你把父目录作为仓库打开，vault 路径就是 `knowledge-system/`。

### 第二步：安装 Local REST API 插件

1. 在 Obsidian 中，打开 **设置**（左下角齿轮图标）
2. 进入 **第三方插件**
3. 关闭「安全模式」（如果还没关闭）
4. 点击「浏览」，搜索 **Local REST API**
5. 找到由 `coddingtonbear` 开发的插件，点击 **安装**
6. 安装完成后点击 **启用**

### 第三步：配置 API

1. 在 Obsidian 设置中，找到 **Local REST API** 插件设置
2. 记下以下信息：
   - **API Key**：一串随机字符串，用于认证请求
   - **Port**：默认端口 `27124`
   - **Host**：默认 `127.0.0.1`

3. 确保以下选项已启用：
   - ✅ **Enable REST API**
   - ✅ **Allow access to all vault files**

### 第四步：配置环境变量（可选）

系统已内置默认 API Key（从插件配置中读取），通常无需手动配置。
如需覆盖，可设置环境变量：

```bash
export OBSIDIAN_API_KEY="your-api-key-here"
export OBSIDIAN_API_BASE="https://127.0.0.1:27124"
export OBSIDIAN_VAULT_PATH="knowledge-system"
```

### 第五步：验证连接

```bash
python tools/ks.py status     # 自动检测模式
python tools/ks.py --api health  # 强制 API 模式健康检查
```

如果 REST API 可用，会显示 `REST API` 模式；否则自动回退到 `本地文件` 模式。

### 第六步：安装 Python 依赖

```bash
pip install requests
```

---

## CLI 命令速查

### 模式控制

```bash
python tools/ks.py status                  # 自动检测模式
python tools/ks.py --local status           # 强制本地模式
python tools/ks.py --api health             # 强制 API 模式
```

### 基础操作

```bash
python tools/ks.py search "关键词"                   # 搜索
python tools/ks.py read knowledge/index/index.md    # 读取文件
python tools/ks.py list knowledge/permanent/concepts/  # 列出目录
python tools/ks.py stats                            # 知识库统计
python tools/ks.py index                            # 查看总索引
```

### 四步流程

```bash
# 摄取
python tools/ks.py ingest --title "标题" --content "正文" --source-url "https://..."

# 消化（准备材料，由 AI Agent 执行）
python tools/ks.py digest --raw raw/2026/04/xxx.md

# 输出（准备上下文，由 AI Agent 执行）
python tools/ks.py output --question "你的问题"

# 巡检
python tools/ks.py inspect
```

### 文件操作

```bash
python tools/ks.py create --file "path.md" --content "# 内容"
python tools/ks.py append --file "path.md" --content "追加内容"
```

### Obsidian 交互（仅 REST API 模式）

```bash
python tools/ks.py open knowledge/index/index.md   # 在 Obsidian 中打开
python tools/ks.py graph                           # 打开知识图谱
```

---

## Python API 速查

### 自动模式（推荐）

```python
from tools.obsidian_client import ObsidianClient
from tools.local_client import LocalClient

# REST API 客户端（自动探测地址）
api_client = ObsidianClient()  # 自动探测宿主机 IP
if api_client.is_available():
    api_client.create_note("knowledge/fleeting/test.md", "# 测试")
    api_client.open_in_obsidian("knowledge/index/index.md")

# 本地文件客户端（无需 Obsidian）
local_client = LocalClient()  # 自动检测知识库目录
local_client.create_note("knowledge/fleeting/test.md", "# 测试")
stats = local_client.get_stats()
broken = local_client.find_broken_links()
```

### REST API 客户端（手动配置）

```python
from tools.obsidian_client import ObsidianClient

client = ObsidianClient(
    api_base="https://127.0.0.1:27124",
    api_key="your-api-key",
    vault_path="knowledge-system",
)
client.health_check()
client.create_note("knowledge/fleeting/test.md", "# 测试\n\n内容")
client.open_knowledge_graph()
```

---

## 双模式能力对比

| 功能 | REST API 模式 | Local 模式 |
|------|:---:|:---:|
| 创建/读取/更新/删除笔记 | ✅ | ✅ |
| 搜索笔记内容 | ✅ | ✅ (grep) |
| 列出目录 | ✅ | ✅ |
| 摄取资料 | ✅ | ✅ |
| 知识库统计 | ✅ | ✅ |
| 断链检查 | ❌ | ✅ |
| 在 Obsidian 中打开文件 | ✅ | ❌ |
| 打开知识图谱 | ✅ | ❌ |
| 执行 Obsidian 命令 | ✅ | ❌ |
| 需要 Obsidian 运行 | ✅ | ❌ |

---

## 安全提示

- API 仅在本地运行（`127.0.0.1`），不会暴露到公网
- API Key 是唯一的认证凭据，请妥善保管
- 插件使用自签名证书，浏览器可能会显示安全警告，可以忽略
- Local 模式直接操作文件系统，无网络安全风险

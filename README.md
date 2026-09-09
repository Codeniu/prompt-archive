# 提示词档 · Prompt Archive

一个提示词收集与归档的小工具，提供两种部署形态：

- **静态版**（`docs/`）：部署到 GitHub Pages，数据存到 GitHub Issues
- **自托管版**（根目录）：单文件 Python 后端，数据存到本地 JSON

两者共用同一套「编辑档案」风格的界面设计。

---

## 形态一：GitHub Pages + Issues（静态版）

适合零成本上线、不需要服务器、数据天然在 GitHub 上可浏览。

**目录**：`docs/index.html`（单文件，无构建步骤）

**数据映射**：

| 操作 | 界面动作 | GitHub API |
| --- | --- | --- |
| 新建 | 「新建条目」→「归档」 | `POST /repos/{owner}/{repo}/issues` |
| 查看 | 点击卡片 | `GET /repos/{owner}/{repo}/issues` |
| 编辑 | 详情页「编辑」→「保存修改」 | `PATCH /repos/{owner}/{repo}/issues/{number}` |
| 删除 | 卡片「销毁」 | `PATCH ...issues/{number}` `state=closed` |

issue 的 `title` = 提示词标题、`body` = 提示词内容、`labels` = 标签。删除即关闭 issue（GitHub 不支持真删）。

### 部署步骤

1. 在 GitHub 新建一个公开仓库（例如 `prompt-archive`），确保 Issues 功能开启（默认开）。
2. 把 `docs/` 目录推到 `main` 分支。
3. 仓库 **Settings → Pages → Build and deployment**，Source 选 `Deploy from a branch`，分支选 `main`，文件夹选 `/docs`，保存。
4. 等 1–2 分钟后访问 `https://<你的用户名>.github.io/<仓库名>/`。
5. 打开页面点右上 ⚙，填用户名、仓库名、Personal Access Token（公开仓库勾选 `public_repo` 即可，[这里创建](https://github.com/settings/tokens/new?scopes=public_repo)），保存。
6. 之后所有提示词都以 issue 形式存到该仓库，也能在 GitHub 的 Issues 页面直接浏览/搜索。

> Token 仅存于浏览器本机 localStorage，不会上传到任何服务器。`public_repo` 即最小权限；私有仓库才需 `repo` 完整权限。请勿在公共设备保存。

---

## 形态二：自托管 Python 版

适合本地使用、内网部署、或不想把数据放到 GitHub 上。

**文件**：`server.py` + `index.html`（根目录）

- 后端：`server.py`，仅用 Python 标准库（无依赖），数据存到同目录 `prompts.json`
- 前端：`index.html`，与静态版共用设计，调本地 `/api/prompts` 接口

### 运行

```bash
python3 server.py
# → Prompt collector running on http://localhost:8000
```

浏览器打开 [http://localhost:8000/](http://localhost:8000/) 即可。

### API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/prompts` | 列出全部提示词 |
| `POST` | `/api/prompts` | 新建（`title`、`content`、`tags`） |
| `PUT` | `/api/prompts/{id}` | 修订（写入 `updated_at`） |
| `DELETE` | `/api/prompts/{id}` | 删除 |

---

## 功能

- 提示词列表（网格卡片布局，编号档案条目风格）
- 顶部固定导航：刊头 + 搜索框 + 新增按钮
- 分类目录：按标签筛选，每标签显示数量
- 点击卡片查看详情，详情页可编辑
- 新增提示词以模态弹窗显示
- 一键复制（誊抄）、删除（销毁）
- 快捷键：`/` 聚焦搜索，`Ctrl/Cmd + Enter` 保存，`Esc` 关闭弹窗

## 设计

「编辑档案」视觉语言：暖米黄纸张底色、朱砂红作为编辑批注章式的强调色（稀缺使用）、Fraunces 衬线标题 + JetBrains Mono 提示词正文 + 系统 sans UI 控件的三联字体。卡片是带编号（`No. 0001`）的档案条目，无阴影无圆角，靠细线分隔；弹窗是直角书写稿纸风格。支持 `prefers-reduced-motion` 与 `:focus-visible` 焦点环。

## 目录结构

```
.
├── docs/
│   └── index.html      # 静态版（GitHub Pages）
├── index.html          # 自托管版前端
├── server.py           # 自托管版后端（stdlib）
└── prompts.json        # 自托管版数据存储（运行时生成）
```

## 许可

MIT

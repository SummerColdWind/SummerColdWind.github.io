# 数据文件说明

日常更新主页时，**编辑 `data/` 下的 JSON**，然后运行构建脚本。

## 目录结构

```
data/
├── shared.json             # 社交链接（中英文共用）
├── publications.json       # ★ 论文列表（中英文共用）
├── zh/
│   └── site.json
└── en/
    └── site.json
```

构建输出：

- 英文（默认）：`index.html`（站点根目录）
- 中文：`zh/index.html`

页头 **中文 | EN** 切换器在两个版本间跳转。

## 文件职责

| 文件 | 更新频率 | 内容 |
|------|----------|------|
| `shared.json` | 低 | Scholar / ORCID / GitHub 等社交链接 |
| `publications.json` | **高** | 论文列表（中英文共用，标题与作者为英文） |
| `site.json` | 低 | 各语言页面文案、导航、区块标题、小游戏 |

**共用数据：** 论文、社交链接改一处即可。简介、导航等仍在 `zh/site.json` 与 `en/site.json` 分别维护。

## 可选区块

**缺失字段或空数据时，对应区块不会出现在页面中**，构建也不会报错。

| 区块 | 显示条件 |
|------|----------|
| Hero | `profile.name` 存在 |
| 关于 | `about.paragraphs` 或 `about.info` 非空 |
| 研究 | `research.items` 非空 |
| 论文 | `publications.json` 存在且含论文 |
| 教学 | `teaching.items` 非空 |
| 联系 | `contact.intro` / `items` / `location` 任一有内容 |
| 小游戏 | `games_section.items` 非空 |
| 导航 | 仅显示已有区块的链接 |
| 头像 | `profile.photo` |
| Email（Hero 社交行） | `profile.email` |
| 社交链接 | `shared.json` 的 `social` + 自动追加 Email |
| 语言切换 | `ui.lang_*` 相关字段齐全 |

**修改 JSON 后必须重新构建** 页面才会更新：

```bash
python scripts/build.py
```

本地开发推荐（保存 JSON 后自动 rebuild）：

```bash
python scripts/serve.py
```

## 常见操作

### 新增一篇论文

编辑 **`data/publications.json`**，在对应年份的 `papers` 数组**最前面**插入：

```json
{
  "title": "Paper Title",
  "authors": [
    { "name": "Qincheng Qiao", "me": true },
    { "name": "Juan Cao", "equal": true }
  ],
  "venue": "NeurIPS",
  "year": 2025,
  "links": [
    { "label": "Paper", "url": "https://doi.org/..." }
  ]
}
```

作者字段：

- `"me": true` — 高亮你的名字
- `"equal": true` — 共同第一作者标记 `†`
- `"corresponding": true` — 通讯作者标记 `*`

**插图：** `figure.src` 指向 `assets/images/pubs/` 下文件；替换图片后运行 build，并确保图片已 `git add`。

### 修改小游戏

在 `site.json` 的 `games_section` 中编辑标题、简介与 `items`（`id` 须与 `assets/js/games.js` 中一致：`reaction`、`memory`、`guess`、`clicks`）。

### 修改 UI 文案

页脚、语言切换等字符串在 `site.json` 的 `ui` 字段。中文版 `lang_other_href` 为 `"../"`。

### 更新邮箱 / 单位

- 邮箱：`profile.email`（两个语言的 `site.json` 同步）
- 单位：`affiliation` 与 `about.paragraphs` 中英文分别维护，注意译名一致
- 社交链接：`data/shared.json`

## 静态资源

| 路径 | 用途 |
|------|------|
| `assets/images/profile.png` | 头像 |
| `assets/images/pubs/*` | 论文缩略图 |

部署前确认这些文件已提交到 git（本地存在 ≠ 已推送）。

## 构建与部署

```bash
python scripts/build.py
git add index.html zh/index.html
git push
```

GitHub Actions（`.github/workflows/build.yml`）会在 push 时检查 HTML 是否与 JSON 同步。

## 设计原则

1. **按语言分目录** — 翻译清晰，互不干扰
2. **静态双页面** — SEO 友好，GitHub Pages 零运行时
3. **相对路径切换** — 英文在 `/`，中文在 `/zh/`

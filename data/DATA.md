# 数据文件说明

日常更新主页时，**编辑 `data/zh/` 或 `data/en/` 下的 JSON**，然后运行构建脚本。

## 目录结构

```
data/
├── shared.json             # 社交链接（中英文共用）
├── publications.json       # ★ 论文列表（中英文共用）
├── zh/
│   ├── site.json
│   └── projects.json
└── en/
    ├── site.json
    └── projects.json
```

构建输出：

- 中文：`index.html`（站点根目录）
- 英文：`en/index.html`

页头 **中文 | EN** 切换器在两个版本间跳转。

## 文件职责

| 文件 | 更新频率 | 内容 |
|------|----------|------|
| `shared.json` | 低 | 社交链接等中英文共用信息 |
| `publications.json` | **高** | 论文列表（中英文共用，作者与标题均为英文） |
| `site.json` | 低 | 各语言页面文案、导航、区块标题 |
| `projects.json` | 中 | 开源项目（按语言分目录） |

**共用数据：** 论文、社交链接只需改一处。区块标题、简介等仍在 `zh/site.json` 与 `en/site.json` 分别维护。

## 可选区块

**缺失字段或空数据时，对应区块不会出现在页面中**，构建也不会报错。

| 区块 | 显示条件 |
|------|----------|
| Hero | `profile.name` 存在 |
| 关于 | `about.paragraphs` 或 `about.info` 非空 |
| 研究 | `research.items` 非空 |
| 论文 | `data/publications.json` 存在且含论文 |
| 项目 | `projects.json` 存在且 `items` 非空 |
| 教学 | `teaching.items` 非空 |
| 联系 | `contact.intro` / `items` / `location` 任一有内容 |
| 导航 | 仅显示已有区块的链接 |
| CV / 邮件按钮 | 分别需 `profile.cv` / `profile.email` |
| 头像 | 需 `profile.photo` |
| 社交链接 | `data/shared.json` 的 `social`（中英文共用） |
| 语言切换 | `ui.lang_*` 相关字段齐全 |

**修改 JSON 后必须重新构建** 页面才会更新：

```bash
python scripts/build.py
```

本地开发推荐（保存 JSON 后自动 rebuild）：

```bash
python scripts/serve.py
# 或 serve.bat
```

删除单个社交链接：编辑 `data/shared.json`，去掉对应条目，或设 `"enabled": false` / `"url": ""`。

`publications.json` / `projects.json` 整个文件可省略。

## 常见操作

### 新增一篇论文

编辑 **`data/publications.json`**（中英文共用），在对应年份的 `papers` 数组**最前面**插入：

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
    { "label": "PDF", "url": "https://doi.org/..." }
  ]
}
```

作者字段：

- `"me": true` — 高亮你的名字
- `"equal": true` — 共同第一作者标记 `†`

**插图占位：** 每篇论文的 `figure.src` 指向 `assets/images/pubs/` 下对应文件。直接替换同名图片（或改 `src` 扩展名），然后运行 build。

```json
"figure": {
  "src": "assets/images/pubs/my-paper-2025.svg",
  "alt": "Teaser figure description",
  "link": "https://doi.org/..."
}
```

### 修改 UI 文案

按钮、页脚、语言切换等字符串在 `site.json` 的 `ui` 字段：

```json
"ui": {
  "download_cv": "下载 CV",
  "lang_current": "中文",
  "lang_other": "EN",
  "lang_other_href": "en/"
}
```

英文版 `en/site.json` 中 `lang_other_href` 为 `"../"`。

### 更新邮箱 / 单位

修改两个语言目录下的 `site.json`，同步 `profile`、`affiliation`、`about.info`、`contact.items`。

## 构建

```bash
python scripts/build.py
```

同时生成 `index.html` 与 `en/index.html`。

## 设计原则

1. **按语言分目录** — 翻译清晰，互不干扰
2. **静态双页面** — SEO 友好，GitHub Pages 零运行时
3. **相对路径切换** — 中英文通过 `/` 与 `/en/` 跳转，适配用户页与项目页

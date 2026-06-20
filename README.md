# 个人学术主页模板

适用于 [GitHub Pages](https://pages.github.com/) 的静态学术主页，支持**中英文切换**。

## 项目结构

```
homepage/
├── data/
│   ├── shared.json         # 社交链接（共用）
│   ├── publications.json   # ★ 论文列表（共用）
│   ├── zh/                 # 中文页面文案
│   └── en/                 # 英文页面文案
├── templates/base.html
├── scripts/build.py
├── index.html              # 中文页（构建产物）
├── en/index.html           # 英文页（构建产物）
└── assets/
```

## 更新工作流

```
编辑 data/zh 或 data/en  →  运行 build  →  git push
```

```bash
python scripts/build.py    # 生成 index.html + en/index.html
build.bat                  # Windows
```

页头 **中文 | EN** 在 `/` 与 `/en/` 间切换。

### 常见场景

| 场景 | 操作 |
|------|------|
| 发新论文 | `data/publications.json` |
| 改中文简介 | `data/zh/site.json` |
| 改英文简介 | `data/en/site.json` |
| 共享信息（邮箱、链接） | 两个语言的 `site.json` 都改 |

详细说明见 [data/DATA.md](data/DATA.md)。

## 本地预览

```bash
python scripts/build.py
python -m http.server 8000
```

- 中文：http://localhost:8000/
- 英文：http://localhost:8000/en/

## 部署

推送前运行 `python scripts/build.py`，确保 `index.html` 与 `en/index.html` 已更新。

## 特性

- 中英文独立数据，静态双页面（SEO 友好）
- 论文插图、结构化作者列表
- 数据与模板分离，GitHub Pages 零运行时

## 许可

模板可自由修改与使用。

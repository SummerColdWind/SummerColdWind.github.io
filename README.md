# 乔亲成 · 学术主页

适用于 [GitHub Pages](https://pages.github.com/) 的静态学术主页，支持**中英文切换**。

## 项目结构

```
homepage/
├── data/
│   ├── shared.json         # 社交链接（中英文共用）
│   ├── publications.json   # 论文列表（中英文共用）
│   ├── zh/site.json        # 中文页面文案
│   └── en/site.json        # 英文页面文案
├── assets/                 # 样式、脚本、图片、PDF
├── templates/base.html
├── scripts/build.py
├── index.html              # 中文页（构建产物）
├── en/index.html           # 英文页（构建产物）
└── .nojekyll               # GitHub Pages 禁用 Jekyll
```

## 更新工作流

```
编辑 data/  →  python scripts/build.py  →  git push
```

```bash
python scripts/build.py    # 或 build.bat
```

页头 **中文 | EN** 在 `/` 与 `/en/` 间切换。

### 常见场景

| 场景 | 操作 |
|------|------|
| 发新论文 | `data/publications.json` |
| 改中文简介 | `data/zh/site.json` |
| 改英文简介 | `data/en/site.json` |
| 社交链接 | `data/shared.json` |
| 邮箱 | 两个语言的 `site.json` → `profile.email` |

详细说明见 [data/DATA.md](data/DATA.md)。

## 本地预览

```bash
python scripts/serve.py    # 或 serve.bat，保存 data/ 后自动 rebuild
```

- 中文：http://localhost:11454/
- 英文：http://localhost:11454/en/

## 部署到 GitHub Pages

1. 修改 JSON / 资源后运行 `python scripts/build.py`
2. 提交并推送 `index.html`、`en/index.html` 及 `assets/` 等变更
3. 仓库 **Settings → Pages → Build and deployment**：
   - Source: **Deploy from a branch**
   - Branch: **main** / **/ (root)**
4. 站点地址：`https://<username>.github.io/<repo>/`（用户主页仓库则为 `https://<username>.github.io/`）

推送前请确认 `assets/images/` 下头像与论文缩略图已纳入 git。

## 特性

- 中英文独立数据，静态双页面（SEO 友好）
- 论文插图、结构化作者列表
- 页底趣味小游戏（可选，`games_section`）
- 数据与模板分离，GitHub Pages 零运行时
- CI 校验构建产物是否与 JSON 同步

## 许可

可自由修改与使用。

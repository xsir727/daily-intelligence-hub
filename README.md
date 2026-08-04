---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 5b780e4c4b600f98173178c622ba8482_8a9fea698f9c11f180ed525400f8a581
    ReservedCode1: BvT1XRVsLyd8i26ltoCOUwYArxmQeCGYoINLZjk6318P3ZAlAXW3RZnfCdoeo8XzRAdvAcByKatlUSbvhRHyugWqc6mkKyYaZWqBfpMg6mKOLTEk8/GzxNScY0s9gOnHwYMcBiQz7OqA72NuPcNrO3OBFVcT14muKojISc6/wVG6gOG1H3/5buUtQgg=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 5b780e4c4b600f98173178c622ba8482_8a9fea698f9c11f180ed525400f8a581
    ReservedCode2: BvT1XRVsLyd8i26ltoCOUwYArxmQeCGYoINLZjk6318P3ZAlAXW3RZnfCdoeo8XzRAdvAcByKatlUSbvhRHyugWqc6mkKyYaZWqBfpMg6mKOLTEk8/GzxNScY0s9gOnHwYMcBiQz7OqA72NuPcNrO3OBFVcT14muKojISc6/wVG6gOG1H3/5buUtQgg=
---

# Daily Intelligence Hub - 每日情报聚合站

自动聚合**自然资源动态**、**海域陆域研究**、**AI行业进展**、**社科人文热点**的 GitHub Pages 网站。深蓝黑色星际空间主题 UI，带动态星云效果和 Canvas 粒子星空背景。

## 功能特性

- **自然资源动态**：来源自然资源部及各省市区县自然资源系统，每日 15~20 条摘要
- **海域陆域研究专题**：每日精选 5 篇，优先 3 日内最新
- **AI行业进展**：每日 5 条，按时间倒序
- **社科人文热点**：来自社科、人文、教育、书籍领域的今日资讯，共 10 条
- **留言板**：基于 utterances，使用 GitHub Issues 作为评论后端
- **星际空间主题 UI**：深蓝黑色背景 + CSS 动画星云 + Canvas 粒子星空
- **定时自动更新**：GitHub Actions 每天北京时间 8:00 自动运行爬虫

## 部署步骤

### 1. Fork 或创建 GitHub 仓库

将本项目上传到你的 GitHub 仓库。

### 2. 启用 GitHub Pages

在仓库 `Settings → Pages` 中：
- Source 选择 `Deploy from a branch`
- Branch 选择 `main`，目录选择 `/ (root)`
- 点击 Save

### 3. 启用 Actions 权限

在仓库 `Settings → Actions → General` 中：
- 选择 `Read and write permissions`
- 勾选 `Allow GitHub Actions to create and approve pull requests`
- 点击 Save

### 4. 安装 utterances app

访问 [utterances app](https://github.com/apps/utterances) 安装到你的仓库。

### 5. 替换占位符

编辑 `index.html`，将以下内容：
```
repo="YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```
替换为你的实际 GitHub 用户名和仓库名（例如 `repo="zhangsan/daily-intelligence-hub"`）。

### 6. 等待自动更新

GitHub Actions 会在每天北京时间 8:00 自动运行爬虫。你也可以在 Actions 页面手动触发 `Daily Intelligence Scrape`。

## 项目结构

```
daily-intelligence-hub/
├── index.html              # 主页面
├── css/
│   └── style.css           # 星际空间主题样式
├── js/
│   └── main.js             # 星空粒子 + 数据渲染
├── data/
│   ├── natural-resources.json  # 自然资源动态（爬虫产出）
│   ├── marine-land.json        # 海域陆域专题（爬虫产出）
│   ├── ai.json                 # AI行业进展（爬虫产出）
│   └── social-science.json     # 社科人文热点（爬虫产出）
├── scraper/
│   └── scraper.py          # Python 爬虫脚本
├── .github/workflows/
│   └── daily-scrape.yml    # GitHub Actions 定时任务
├── requirements.txt        # Python 依赖
└── README.md               # 本文件
```

## 本地运行爬虫

```bash
pip install -r requirements.txt
python scraper/scraper.py
```

## 技术栈

- **前端**：HTML5 / CSS3 / Vanilla JavaScript (Canvas API)
- **爬虫**：Python + requests + BeautifulSoup + lxml
- **CI/CD**：GitHub Actions
- **评论**：utterances (GitHub Issues)
- **托管**：GitHub Pages
*（内容由AI生成，仅供参考）*

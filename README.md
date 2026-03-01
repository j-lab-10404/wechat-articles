# 📚 微信公众号文章知识库

将微信公众号文章转化为结构化知识库。粘贴文章链接，AI 自动分析、分类、提取论文和数据集信息。

**在线体验：** https://wechat-articles.vercel.app

---

## 系统架构

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   Vue 3 前端     │────▶│   FastAPI 后端        │────▶│  PostgreSQL     │
│   (Vercel)      │ API │   (Render)            │     │  (Neon)         │
└─────────────────┘     └──────┬───────┬────────┘     └─────────────────┘
                               │       │
                    ┌──────────┘       └──────────┐
                    ▼                              ▼
          ┌─────────────────┐           ┌──────────────────┐
          │  WeWe-RSS       │           │  AI API          │
          │  (Railway)      │           │  (ModelScope)    │
          │  订阅管理+全文   │           │  文章分析+分类    │
          └─────────────────┘           └──────────────────┘
```

## 核心功能

### 文章管理
- 粘贴微信公众号文章链接，自动获取全文内容
- 文章列表浏览，支持按类型、标签筛选
- 全文搜索、收藏、标签管理

### AI 智能分析
- 自动分类：论文解读 / 数据集 / 工具 / 教程 / 资讯
- 生成中文摘要（200字以内）
- 提取关键词和标签（5-10个，面向学术领域）
- 从论文解读类文章中提取论文信息（标题、作者、DOI、arXiv ID）
- 从数据集类文章中提取数据集信息（名称、类型、规模、下载链接）

### 论文库
- 自动从文章中提取的学术论文信息
- 含 DOI 链接、arXiv 链接、PDF 下载
- 支持搜索，可追溯来源文章

### 数据集库
- 自动从文章中提取的公开数据集信息
- 含数据类型、规模、领域、下载方式
- 支持搜索，可追溯来源文章

---

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + TypeScript + Element Plus | SPA，Vite 构建 |
| 后端 | FastAPI + SQLAlchemy | Python 异步 API |
| 数据库 | PostgreSQL (JSONB) | 标签、关键词等用 JSONB 存储 |
| AI | OpenAI 兼容 API | 支持 GPT-4 / DeepSeek / Kimi 等 |
| 内容获取 | WeWe-RSS + 直接抓取 | 双重策略，优先直接抓取 |
| 部署 | Vercel + Render + Neon + Railway | 全免费方案 |

---

## 项目结构

```
wechat-articles/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── articles.py     # 文章 CRUD、添加、分析、标签、收藏、搜索
│   │   │   ├── papers.py       # 论文列表、搜索
│   │   │   ├── datasets.py     # 数据集列表、搜索
│   │   │   ├── accounts.py     # 公众号账户管理
│   │   │   └── knowledge.py    # 知识库接口
│   │   ├── models/             # SQLAlchemy 数据模型
│   │   │   ├── article.py      # 文章（标题、内容、标签、分类、摘要）
│   │   │   ├── paper.py        # 论文（标题、作者、DOI、arXiv、PDF链接）
│   │   │   ├── dataset.py      # 数据集（名称、类型、规模、下载链接）
│   │   │   └── analysis.py     # AI 分析结果
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑
│   │   │   ├── ai_service.py   # AI 分析（分类、摘要、提取论文/数据集）
│   │   │   └── rss_service.py  # 内容获取（直接抓取 + WeWe-RSS 回退）
│   │   ├── config.py           # 配置（环境变量）
│   │   ├── database.py         # 数据库连接
│   │   └── main.py             # FastAPI 应用入口
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue        # 首页（统计、快捷入口、最近文章）
│   │   │   ├── AddArticle.vue  # 添加文章（粘贴链接、自动分析）
│   │   │   ├── Articles.vue    # 文章列表（筛选、搜索、收藏、删除）
│   │   │   ├── ArticleDetail.vue # 文章详情（摘要、标签、论文、数据集、正文）
│   │   │   ├── Papers.vue      # 论文库
│   │   │   └── Datasets.vue    # 数据集库
│   │   ├── api/client.ts       # Axios HTTP 客户端
│   │   ├── router/index.ts     # Vue Router 路由
│   │   └── App.vue             # 根组件（导航栏）
│   ├── index.html
│   └── package.json
├── docker/                     # Docker 配置
│   ├── backend.Dockerfile
│   └── docker-compose.yml      # 本地开发全套环境
├── docker-compose.wewe-rss.yml # WeWe-RSS 独立部署
├── vercel.json                 # Vercel 前端部署 + API 代理
└── render.yaml                 # Render 后端部署
```

---

## API 接口

### 文章

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/articles/add` | 添加文章（URL + 自动获取内容 + AI 分析） |
| `GET` | `/api/articles/` | 文章列表（支持 article_type / label / is_favorite 筛选） |
| `GET` | `/api/articles/{id}` | 文章详情（含论文、数据集、分析结果） |
| `DELETE` | `/api/articles/{id}` | 删除文章 |
| `GET` | `/api/articles/search/?q=xxx` | 全文搜索 |
| `POST` | `/api/articles/{id}/analyze` | 重新 AI 分析 |
| `POST` | `/api/articles/{id}/fetch-content` | 重新获取内容 |
| `POST` | `/api/articles/{id}/favorite` | 切换收藏状态 |
| `PUT` | `/api/articles/{id}/labels` | 修改标签 |
| `POST` | `/api/articles/{id}/labels/add?label=xxx` | 添加标签 |
| `DELETE` | `/api/articles/{id}/labels/{label}` | 删除标签 |
| `GET` | `/api/articles/labels` | 获取所有标签及计数 |

### 论文 & 数据集

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/papers/?q=xxx` | 论文列表（支持搜索） |
| `GET` | `/api/datasets/?q=xxx` | 数据集列表（支持搜索） |

---

## 数据模型

### Article（文章）
- `title` 标题、`url` 原文链接、`author` 公众号名称
- `content` HTML 全文、`content_text` 纯文本
- `article_type` 分类（paper_review / dataset / tool / tutorial / news / other）
- `summary` AI 摘要、`keywords` 关键词（JSONB）
- `labels` 标签（JSONB，AI 自动 + 用户手动）
- `is_favorite` 收藏状态

### Paper（论文）
- `title` 英文标题、`title_cn` 中文标题
- `authors` 作者列表、`journal` 期刊/会议、`year` 年份
- `doi` DOI、`arxiv_id` arXiv ID
- `abstract` 摘要、`main_findings` 主要发现
- `pdf_url` PDF 链接、`source_url` 原文链接

### Dataset（数据集）
- `name` 名称、`description` 简介
- `data_type` 数据类型、`scale` 规模、`domain` 领域
- `download_url` 下载链接、`access_method` 获取方式
- `tutorial` 获取教程

---

## 内容获取策略

系统采用双重策略获取微信文章内容：

1. **直接抓取**（优先）：使用移动端 User-Agent 直接请求微信文章页面，解析 `#js_content` 提取正文。速度快（3-6秒），但从部分云服务器 IP 可能被微信拦截。

2. **WeWe-RSS 回退**：当直接抓取失败时，遍历已订阅的 WeWe-RSS feeds，通过 URL 匹配找到对应文章，从 `content_html` 中提取纯文本。需要文章来源公众号已在 WeWe-RSS 中订阅。

---

## 部署指南

### 当前线上环境

| 服务 | 平台 | URL |
|------|------|-----|
| 前端 | Vercel | https://wechat-articles.vercel.app |
| 后端 | Render (Free) | https://wechat-articles-backend.onrender.com |
| 数据库 | Neon (Free PostgreSQL) | ap-southeast-1 |
| WeWe-RSS | Railway | https://wewe-rss-production-d5fc.up.railway.app |
| AI API | ModelScope | Kimi K2.5 |

> Render 免费版有 30 秒请求超时限制和冷启动（约 50 秒）。首次访问可能较慢。

### 从零部署

#### 1. 数据库（Neon）

1. 注册 [Neon](https://neon.tech)，创建 PostgreSQL 数据库
2. 获取连接字符串：`postgresql://user:pass@host/dbname?sslmode=require`

#### 2. WeWe-RSS（Railway）

1. 注册 [Railway](https://railway.app)
2. 部署 MySQL + WeWe-RSS Docker 镜像 `cooderl/wewe-rss:latest`
3. 设置环境变量：`AUTH_CODE`、`FEED_MODE=fulltext`
4. 在 WeWe-RSS 管理界面添加公众号订阅

或本地部署：
```bash
docker-compose -f docker-compose.wewe-rss.yml up -d
```

#### 3. 后端（Render）

1. Fork 本仓库到你的 GitHub
2. 注册 [Render](https://render.com)，创建 Web Service，连接 GitHub 仓库
3. 设置：
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. 配置环境变量：

```env
DATABASE_URL=postgresql://...          # Neon 连接字符串
SECRET_KEY=随机字符串
WEWE_RSS_URL=https://your-wewe-rss.up.railway.app
WEWE_RSS_AUTH_CODE=你的认证码
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1   # 或其他兼容API
OPENAI_MODEL=moonshotai/Kimi-K2.5                        # 或其他模型
CORS_ORIGINS=https://your-frontend.vercel.app
```

#### 4. 前端（Vercel）

1. 注册 [Vercel](https://vercel.com)，导入 GitHub 仓库
2. 设置：
   - Framework Preset: Vue.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
3. `vercel.json` 已配置 API 代理到 Render 后端

#### 5. 本地开发

```bash
# 后端
cd backend
cp .env.example .env   # 编辑 .env 填入配置
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端
cd frontend
npm install
npm run dev
```

---

## AI API 配置

系统使用 OpenAI 兼容接口，支持多种 AI 服务：

| 服务 | OPENAI_BASE_URL | OPENAI_MODEL | 说明 |
|------|-----------------|--------------|------|
| ModelScope | `https://api-inference.modelscope.cn/v1` | `moonshotai/Kimi-K2.5` | 免费，推荐 |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 便宜 |
| OpenAI | `https://api.openai.com/v1` | `gpt-4-turbo-preview` | 效果好，贵 |
| Groq | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile` | 免费 |

---

## 致谢

- [WeWe-RSS](https://github.com/cooderl/wewe-rss) — 微信公众号 RSS 订阅服务
- [FastAPI](https://fastapi.tiangolo.com/) — Python 异步 Web 框架
- [Vue 3](https://vuejs.org/) + [Element Plus](https://element-plus.org/) — 前端框架和 UI 组件库
- [Neon](https://neon.tech) — 免费 Serverless PostgreSQL

## 联系

- Email: liujie@njfu.edu.cn
- GitHub: [@j-lab-10404](https://github.com/j-lab-10404)

## License

MIT

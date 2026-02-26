# 🔑 环境变量完整清单

部署前先准备好所有环境变量，然后统一配置。

---

## 📋 环境变量清单

### 必需的环境变量（7个）

| 变量名 | 说明 | 示例值 | 获取方式 |
|--------|------|--------|----------|
| `DATABASE_URL` | PostgreSQL 连接字符串 | `postgresql://user:pass@host/db?sslmode=require` | 从 Neon 获取 |
| `OPENAI_API_KEY` | AI API 密钥 | `sk-xxxxx` | 从 DeepSeek/OpenAI 获取 |
| `OPENAI_BASE_URL` | AI API 地址 | `https://api.deepseek.com/v1` | 根据 AI 服务商 |
| `OPENAI_MODEL` | AI 模型名称 | `deepseek-chat` | 根据 AI 服务商 |
| `SECRET_KEY` | 应用密钥 | 随机字符串 | 自己生成 |
| `CORS_ORIGINS` | 前端地址 | `https://your-app.vercel.app` | 你的 Vercel URL |
| `SCRAPERAPI_KEY` | 抓取服务密钥 | `xxxxx` | 从 ScraperAPI 获取 |

### 可选的环境变量（2个）

| 变量名 | 说明 | 默认值 | 获取方式 |
|--------|------|--------|----------|
| `REDIS_URL` | Redis 连接字符串 | 无 | 从 Upstash 获取 |
| `WEWE_RSS_URL` | RSS 服务地址 | `http://localhost:4000` | 暂时用默认值 |

---

## 📝 获取步骤

### 1️⃣ DATABASE_URL（PostgreSQL）

**服务商：Neon（免费）**

#### 步骤：

1. **注册 Neon**
   ```
   网址：https://neon.tech/
   方式：用 GitHub 账号登录
   ```

2. **创建项目**
   ```
   点击：Create a project
   项目名：wechat-articles
   区域：Asia Pacific (Singapore)
   ```

3. **获取连接字符串**
   ```
   位置：项目首页 → Connection Details
   格式：postgresql://[user]:[password]@[host]/[database]?sslmode=require
   
   示例：
   postgresql://neondb_owner:abc123@ep-cool-sun-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```

4. **记录下来**
   ```
   DATABASE_URL=postgresql://neondb_owner:abc123@ep-cool-sun-123456.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
   ```

---

### 2️⃣ OPENAI_API_KEY + BASE_URL + MODEL

**推荐：DeepSeek（便宜）**

#### 方案 A：DeepSeek（推荐）⭐⭐⭐⭐⭐

**优点：**
- 💰 便宜：比 OpenAI 便宜 90%
- 🇨🇳 国内可用
- 🚀 速度快

**步骤：**

1. **注册 DeepSeek**
   ```
   网址：https://platform.deepseek.com/
   方式：手机号注册
   ```

2. **充值**
   ```
   位置：账户 → 充值
   金额：最低 10 元（可以用很久）
   方式：支付宝/微信
   ```

3. **创建 API Key**
   ```
   位置：API Keys → 创建新密钥
   复制：sk-xxxxx
   ```

4. **记录下来**
   ```
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   OPENAI_MODEL=deepseek-chat
   ```

#### 方案 B：Groq（免费但需科学上网）

**优点：**
- 💰 完全免费
- 🚀 速度超快

**步骤：**

1. **注册 Groq**
   ```
   网址：https://console.groq.com/
   方式：Google 账号登录
   ```

2. **创建 API Key**
   ```
   位置：API Keys → Create API Key
   复制：gsk_xxxxx
   ```

3. **记录下来**
   ```
   OPENAI_API_KEY=gsk_xxxxx
   OPENAI_BASE_URL=https://api.groq.com/openai/v1
   OPENAI_MODEL=llama-3.1-70b-versatile
   ```

#### 方案 C：OpenAI（最贵）

**步骤：**

1. **注册 OpenAI**
   ```
   网址：https://platform.openai.com/
   需要：国外信用卡
   ```

2. **创建 API Key**
   ```
   位置：API Keys → Create new secret key
   复制：sk-xxxxx
   ```

3. **记录下来**
   ```
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENAI_MODEL=gpt-4-turbo-preview
   ```

---

### 3️⃣ SECRET_KEY（应用密钥）

**用途：** 加密和安全验证

#### 步骤：

1. **生成随机字符串**
   ```
   方法 1：在线生成
   网址：https://randomkeygen.com/
   选择：Fort Knox Passwords（最长的那个）
   
   方法 2：命令行生成
   # Python
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # OpenSSL
   openssl rand -base64 32
   ```

2. **记录下来**
   ```
   SECRET_KEY=your-random-secret-key-here-change-in-production-abc123xyz789
   ```

---

### 4️⃣ CORS_ORIGINS（前端地址）

**用途：** 允许前端访问后端 API

#### 步骤：

1. **获取 Vercel URL**
   ```
   位置：Vercel Dashboard → 你的项目
   格式：https://wechat-articles-xxx.vercel.app
   
   或者在部署成功页面复制
   ```

2. **记录下来**
   ```
   CORS_ORIGINS=https://wechat-articles-xxx.vercel.app
   ```

---

### 6️⃣ SCRAPERAPI_KEY（抓取服务）

**服务商：ScraperAPI（免费试用）**

**用途：** 绕过微信文章的反爬虫保护

#### 步骤：

1. **注册 ScraperAPI**
   ```
   网址：https://www.scraperapi.com/
   方式：用邮箱注册（或 Google 账号登录）
   ```

2. **获取免费试用**
   ```
   免费额度：5,000 次请求
   无需信用卡
   ```

3. **获取 API Key**
   ```
   位置：Dashboard → API Key
   复制：显示的 API Key
   
   格式：一串字母数字组合
   ```

4. **记录下来**
   ```
   SCRAPERAPI_KEY=your_scraperapi_key_here
   ```

**说明：**
- ScraperAPI 提供代理服务，可以绕过微信的反爬虫机制
- 免费试用 5,000 次请求，足够测试和小规模使用
- 如果不配置此项，系统会尝试直接抓取（可能失败）

---

### 7️⃣ REDIS_URL（可选）

**服务商：Upstash（免费）**

#### 步骤：

1. **注册 Upstash**
   ```
   网址：https://upstash.com/
   方式：用 GitHub 账号登录
   ```

2. **创建 Redis 数据库**
   ```
   点击：Create Database
   名称：wechat-articles-redis
   类型：Regional
   区域：选择离你最近的
   ```

3. **获取连接 URL**
   ```
   位置：数据库详情页 → REST API
   复制：UPSTASH_REDIS_REST_URL
   
   格式：https://xxx.upstash.io
   ```

4. **记录下来**
   ```
   REDIS_URL=https://xxx.upstash.io
   ```

**注意：** 如果暂时不用 Redis，可以先不设置，后端会自动跳过。

---

### 8️⃣ WEWE_RSS_URL（可选）

**用途：** 微信公众号 RSS 服务

#### 暂时使用默认值：

```
WEWE_RSS_URL=http://localhost:4000
```

**说明：** 
- 这个服务需要单独部署
- 暂时先用默认值
- 后面再配置

---

## 📄 完整的环境变量模板

### 复制这个模板，填入你的值：

```bash
# ========================================
# 数据库配置
# ========================================
DATABASE_URL=postgresql://[填入你的Neon连接字符串]

# ========================================
# AI API 配置（选择一个方案）
# ========================================
# 方案 A：DeepSeek（推荐）
OPENAI_API_KEY=sk-[填入你的DeepSeek API Key]
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 方案 B：Groq（免费）
# OPENAI_API_KEY=gsk-[填入你的Groq API Key]
# OPENAI_BASE_URL=https://api.groq.com/openai/v1
# OPENAI_MODEL=llama-3.1-70b-versatile

# 方案 C：OpenAI（最贵）
# OPENAI_API_KEY=sk-[填入你的OpenAI API Key]
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4-turbo-preview

# ========================================
# 抓取服务配置
# ========================================
SCRAPERAPI_KEY=[填入你的ScraperAPI Key]

# ========================================
# 应用配置
# ========================================
SECRET_KEY=[填入随机生成的密钥]
CORS_ORIGINS=https://[填入你的Vercel URL]
DEBUG=False

# ========================================
# 可选配置
# ========================================
REDIS_URL=https://[填入你的Upstash URL]
WEWE_RSS_URL=http://localhost:4000
```
# OPENAI_MODEL=llama-3.1-70b-versatile

# 方案 C：OpenAI（最贵）
# OPENAI_API_KEY=sk-[填入你的OpenAI API Key]
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4-turbo-preview

# ========================================
# 应用配置
# ========================================
SECRET_KEY=[填入随机生成的密钥]
CORS_ORIGINS=https://[填入你的Vercel URL]
DEBUG=False

# ========================================
# 可选配置
# ========================================
REDIS_URL=https://[填入你的Upstash URL]
WEWE_RSS_URL=http://localhost:4000
```

---

## ✅ 检查清单

部署前确认：

- [ ] DATABASE_URL 已获取（Neon）
- [ ] OPENAI_API_KEY 已获取（DeepSeek/Groq/OpenAI）
- [ ] OPENAI_BASE_URL 已设置
- [ ] OPENAI_MODEL 已设置
- [ ] SECRET_KEY 已生成
- [ ] CORS_ORIGINS 已获取（Vercel URL）
- [ ] SCRAPERAPI_KEY 已获取（ScraperAPI）
- [ ] REDIS_URL 已获取（可选）

---

## 📍 下一步

准备好所有环境变量后：

1. **部署后端到 Render**
   - 访问：https://render.com/
   - 创建 Web Service
   - 粘贴环境变量

2. **初始化数据库**
   - 在 Render Shell 中运行初始化命令

3. **连接前后端**
   - 在 Vercel 中设置后端 URL

详细步骤见：[DEPLOY_BACKEND_NOW.md](DEPLOY_BACKEND_NOW.md)

---

## 💡 提示

### 安全建议：
- ✅ 不要把环境变量提交到 Git
- ✅ 定期更换 SECRET_KEY
- ✅ 不要分享 API Key

### 费用估算：
- Neon（数据库）：免费
- Upstash（Redis）：免费
- Render（后端）：免费
- DeepSeek（AI）：~10元
- **总计：约 10 元**

### 时间估算：
- 获取所有环境变量：15 分钟
- 部署后端：5 分钟
- 初始化和测试：5 分钟
- **总计：约 25 分钟**

---

需要帮助？
- 提交 Issue: https://github.com/j-lab-10404/wechat-articles/issues
- 发送邮件: liujie@njfu.edu.cn

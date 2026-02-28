# 🚀 WeWe-RSS 部署指南

WeWe-RSS 是一个基于微信读书的公众号订阅服务，可以将微信公众号转换为 RSS 源。

## 📋 项目信息

- **GitHub**: https://github.com/cooderl/wewe-rss
- **Stars**: 8.6k+
- **原理**: 基于微信读书获取公众号文章
- **优点**: 稳定、支持历史文章、自动更新

---

## 🎯 快速部署（推荐：Railway）

### 方案 1：Railway 一键部署 ⭐⭐⭐⭐⭐

**最简单，免费，5分钟搞定**

#### 步骤：

1. **访问 Railway**

   ```
   https://railway.app/
   ```
2. **登录**

   - 用 GitHub 账号登录
3. **部署 MySQL 数据库**

   - 点击 "New Project"
   - 选择 "Deploy MySQL"
   - 等待部署完成
   - 复制 `DATABASE_URL`（在 Variables 标签页）
4. **部署 WeWe-RSS**

   - 在同一个 Project 中，点击 "New Service"
   - 选择 "Docker Image"
   - 输入镜像：`cooderl/wewe-rss:latest`
   - 添加环境变量：
     ```
     DATABASE_URL=mysql://root:password@mysql.railway.internal:3306/railway
     AUTH_CODE=你的密码（随便设置）
     SERVER_ORIGIN_URL=https://你的railway域名
     ```
   - 点击 "Deploy"
5. **获取访问地址**

   - 在 Settings → Networking → Generate Domain
   - 复制生成的域名，例如：`https://wewe-rss-production.up.railway.app`
6. **测试访问**

   - 访问：`https://你的域名`
   - 应该能看到 WeWe-RSS 的管理界面

---

### 方案 2：Zeabur 一键部署 ⭐⭐⭐⭐

**也很简单，国内访问快**

#### 步骤：

1. **访问 Zeabur**

   ```
   https://zeabur.com/
   ```
2. **点击一键部署**

   ```
   https://zeabur.com/templates/OKXO3W
   ```
3. **配置环境变量**

   - `AUTH_CODE`: 设置你的密码
   - 其他保持默认
4. **部署完成**

   - 获取访问域名
   - 访问管理界面

---

### 方案 3：本地 Docker 部署 ⭐⭐⭐

**适合本地测试**

#### 步骤：

1. **创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  db:
    image: mysql:8.3.0
    container_name: wewe-rss-db
    environment:
      MYSQL_ROOT_PASSWORD: 123456
      MYSQL_DATABASE: wewe-rss
      TZ: Asia/Shanghai
    volumes:
      - db_data:/var/lib/mysql
    command: --mysql-native-password=ON
    networks:
      - wewe-rss

  server:
    image: cooderl/wewe-rss:latest
    container_name: wewe-rss-server
    ports:
      - "4000:4000"
    environment:
      DATABASE_URL: mysql://root:123456@db:3306/wewe-rss?schema=public&connect_timeout=30&pool_timeout=30&socket_timeout=30
      AUTH_CODE: 123567
      SERVER_ORIGIN_URL: http://localhost:4000
    depends_on:
      - db
    networks:
      - wewe-rss

networks:
  wewe-rss:
    driver: bridge

volumes:
  db_data:
```

2. **启动服务**

```bash
docker-compose up -d
```

3. **访问**

```
http://localhost:4000
```

---

## 📱 使用 WeWe-RSS

### 1. 添加微信读书账号

1. 访问 WeWe-RSS 管理界面
2. 进入"账号管理"
3. 点击"添加账号"
4. 用微信扫码登录微信读书
5. **重要**：不要勾选"24小时后自动退出"

### 2. 订阅公众号

1. 在微信中打开公众号
2. 点击右上角"..."
3. 点击"分享"
4. 复制链接
5. 在 WeWe-RSS 中进入"公众号源"
6. 点击"添加"
7. 粘贴链接
8. 等待抓取完成

**注意**：添加频率过高容易被封控，建议间隔一段时间添加

### 3. 获取 RSS 地址

订阅成功后，可以获取 RSS 地址：

```
# 单个公众号
https://你的域名/feeds/MP_WXS_123.rss

# 所有公众号
https://你的域名/feeds/all.rss

# JSON 格式
https://你的域名/feeds/all.json

# Atom 格式
https://你的域名/feeds/all.atom
```

---

## 🔗 连接到我们的应用

### 配置后端环境变量

在 Render 中添加环境变量：

```
WEWE_RSS_URL=https://你的wewe-rss域名
WEWE_RSS_AUTH_CODE=你设置的AUTH_CODE
```

### 测试连接

```bash
# 测试 WeWe-RSS 是否正常
curl https://你的域名/feeds/all.json

# 应该返回 JSON 格式的文章列表
```

---

## ⚙️ 环境变量说明

| 变量名                     | 说明                      | 必填 | 默认值        |
| -------------------------- | ------------------------- | ---- | ------------- |
| `DATABASE_URL`           | 数据库连接字符串          | ✅   | -             |
| `AUTH_CODE`              | API 授权码                | ❌   | 空（不启用）  |
| `SERVER_ORIGIN_URL`      | 服务访问地址              | ❌   | -             |
| `MAX_REQUEST_PER_MINUTE` | 每分钟最大请求数          | ❌   | 60            |
| `FEED_MODE`              | 输出模式（fulltext 全文） | ❌   | -             |
| `CRON_EXPRESSION`        | 定时更新表达式            | ❌   | 35 5,17 * * * |

---

## 🔍 高级功能

### 1. 标题过滤

```bash
# 包含"张三"的文章
https://你的域名/feeds/all.atom?title_include=张三

# 包含"张三"或"李四"或"王五"
https://你的域名/feeds/all.atom?title_include=张三|李四|王五

# 排除"张三丰"和"赵六"
https://你的域名/feeds/all.atom?title_exclude=张三丰|赵六

# 组合使用
https://你的域名/feeds/all.atom?title_include=AI&title_exclude=广告
```

### 2. 手动更新

```bash
# 触发单个公众号更新
https://你的域名/feeds/MP_WXS_123.rss?update=true
```

### 3. 限制数量

```bash
# 只返回最新 30 篇
https://你的域名/feeds/all.json?limit=30
```

---

## ⚠️ 注意事项

### 账号状态

| 状态       | 说明       | 解决方案         |
| ---------- | ---------- | ---------------- |
| 今日小黑屋 | 账号被封控 | 等24小时自动恢复 |
| 禁用       | 手动禁用   | 在管理界面启用   |
| 失效       | 登录过期   | 重新扫码登录     |

### 使用建议

1. **不要频繁添加公众号**：容易被封控
2. **多添加几个微信读书账号**：轮流使用
3. **定期检查账号状态**：及时处理失效账号
4. **使用全文模式**：设置 `FEED_MODE=fulltext`

---

## 🧪 测试 WeWe-RSS

创建测试脚本 `test_wewe_rss.py`：

```python
import requests

# WeWe-RSS 地址
WEWE_RSS_URL = "https://你的域名"
AUTH_CODE = "你的AUTH_CODE"

# 测试获取所有文章
response = requests.get(
    f"{WEWE_RSS_URL}/feeds/all.json",
    headers={"Authorization": f"Bearer {AUTH_CODE}"} if AUTH_CODE else {}
)

print(f"状态码: {response.status_code}")
print(f"文章数量: {len(response.json().get('items', []))}")

# 打印前3篇文章
for item in response.json().get('items', [])[:3]:
    print(f"\n标题: {item.get('title')}")
    print(f"链接: {item.get('url')}")
    print(f"发布时间: {item.get('date_published')}")
```

---

## 📊 与我们应用的集成

### 后端 RSSService 已经准备好

我们的后端已经有 `RSSService`，可以直接使用：

```python
from app.services.rss_service import RSSService

# 创建服务
rss_service = RSSService()

# 同步文章
await rss_service.sync_articles(account_id=1)
```

### 前端添加同步按钮

在"公众号管理"页面添加"同步文章"按钮，调用后端 API。

---

## 🎯 下一步

1. ✅ 部署 WeWe-RSS（Railway/Zeabur）
2. ✅ 添加微信读书账号
3. ✅ 订阅几个公众号测试
4. ✅ 配置后端环境变量
5. ✅ 测试 RSS 接口
6. ✅ 在前端添加同步功能

---

## 💡 提示

### 为什么选择 WeWe-RSS？

- ✅ 基于微信读书，更稳定
- ✅ 支持获取历史文章
- ✅ 自动定时更新
- ✅ 支持全文输出
- ✅ 开源免费
- ✅ 8.6k+ stars，活跃维护

### 费用估算

- Railway: 免费（有限额）
- Zeabur: 免费（有限额）
- 本地部署: 免费

---

## 📞 需要帮助？

- **WeWe-RSS 文档**: https://github.com/cooderl/wewe-rss
- **项目 Issues**: https://github.com/j-lab-10404/wechat-articles/issues
- **邮件**: liujie@njfu.edu.cn

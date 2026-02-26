# 🚀 快速启动 WeWe-RSS

## 方式 1：本地 Docker 部署（推荐测试）

### 1. 启动服务

```bash
# 在 wechat-articles 目录下运行
docker-compose -f docker-compose.wewe-rss.yml up -d
```

### 2. 查看日志

```bash
# 查看服务日志
docker-compose -f docker-compose.wewe-rss.yml logs -f wewe-rss-server

# 查看数据库日志
docker-compose -f docker-compose.wewe-rss.yml logs -f wewe-rss-db
```

### 3. 访问管理界面

```
http://localhost:4000
```

### 4. 测试服务

```bash
python test_wewe_rss.py
```

### 5. 停止服务

```bash
docker-compose -f docker-compose.wewe-rss.yml down
```

### 6. 完全清理（包括数据）

```bash
docker-compose -f docker-compose.wewe-rss.yml down -v
```

---

## 方式 2：Railway 云部署（推荐生产）

### 1. 访问 Railway

```
https://railway.app/
```

### 2. 登录

用 GitHub 账号登录

### 3. 创建新项目

- 点击 "New Project"
- 选择 "Deploy MySQL"
- 等待部署完成

### 4. 添加 WeWe-RSS 服务

- 在同一个 Project 中
- 点击 "New Service"
- 选择 "Docker Image"
- 输入：`cooderl/wewe-rss:latest`

### 5. 配置环境变量

点击 WeWe-RSS 服务 → Variables → Add Variable

```
DATABASE_URL=mysql://root:密码@mysql.railway.internal:3306/railway
AUTH_CODE=123567
SERVER_ORIGIN_URL=https://你的域名
```

**注意**：`DATABASE_URL` 从 MySQL 服务的 Variables 中复制

### 6. 生成域名

- Settings → Networking
- 点击 "Generate Domain"
- 复制域名

### 7. 更新 SERVER_ORIGIN_URL

把刚才生成的域名填入 `SERVER_ORIGIN_URL`

### 8. 访问

```
https://你的域名
```

---

## 使用步骤

### 1. 添加微信读书账号

1. 访问 WeWe-RSS 管理界面
2. 点击"账号管理"
3. 点击"添加账号"
4. 用微信扫码登录微信读书
5. **重要**：不要勾选"24小时后自动退出"

### 2. 订阅公众号

1. 在微信中打开任意公众号
2. 点击右上角"..."
3. 点击"分享"
4. 复制链接（例如：`https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=...`）
5. 回到 WeWe-RSS
6. 点击"公众号源"
7. 点击"添加"
8. 粘贴链接
9. 等待抓取完成

**测试公众号推荐**：
- 人民日报
- 新华社
- 36氪
- 虎嗅网

### 3. 查看文章

订阅成功后，等待几分钟，文章会自动同步。

可以通过以下方式查看：

```bash
# 方式 1：浏览器访问
http://localhost:4000/feeds/all.json

# 方式 2：运行测试脚本
python test_wewe_rss.py

# 方式 3：curl 命令
curl http://localhost:4000/feeds/all.json
```

---

## 常见问题

### Q1: 启动失败，提示端口被占用

**解决方案**：修改 `docker-compose.wewe-rss.yml` 中的端口

```yaml
ports:
  - "4001:4000"  # 改成 4001 或其他未占用端口
```

### Q2: 数据库连接失败

**解决方案**：等待数据库完全启动

```bash
# 查看数据库日志
docker-compose -f docker-compose.wewe-rss.yml logs wewe-rss-db

# 重启服务
docker-compose -f docker-compose.wewe-rss.yml restart wewe-rss-server
```

### Q3: 添加公众号失败

**可能原因**：
1. 链接格式不正确（必须是公众号主页链接）
2. 添加频率过高（等24小时）
3. 账号被封控（查看账号状态）

**解决方案**：
- 使用正确的公众号分享链接
- 间隔一段时间再添加
- 添加多个微信读书账号轮流使用

### Q4: 文章不更新

**解决方案**：
1. 检查账号状态（是否在"小黑屋"）
2. 手动触发更新：访问 `http://localhost:4000/feeds/all.rss?update=true`
3. 查看日志：`docker-compose -f docker-compose.wewe-rss.yml logs -f`

### Q5: 如何获取单个公众号的 RSS？

在"公众号源"页面，每个公众号都有对应的 Feed ID（例如：`MP_WXS_123`）

RSS 地址：
```
http://localhost:4000/feeds/MP_WXS_123.rss
http://localhost:4000/feeds/MP_WXS_123.json
http://localhost:4000/feeds/MP_WXS_123.atom
```

---

## 高级配置

### 启用全文模式

修改 `docker-compose.wewe-rss.yml`：

```yaml
environment:
  FEED_MODE: fulltext
```

**注意**：全文模式会让接口响应变慢，占用更多内存

### 修改更新频率

默认每天 5:35 和 17:35 更新

修改 `CRON_EXPRESSION`：

```yaml
environment:
  # 每小时更新一次
  CRON_EXPRESSION: "0 * * * *"
  
  # 每天 8:00 和 20:00 更新
  CRON_EXPRESSION: "0 8,20 * * *"
```

### 限制请求频率

```yaml
environment:
  MAX_REQUEST_PER_MINUTE: 30  # 每分钟最多 30 次请求
```

---

## 连接到我们的应用

### 1. 配置后端环境变量

在 Render 中添加：

```
WEWE_RSS_URL=http://localhost:4000
WEWE_RSS_AUTH_CODE=123567
```

如果是 Railway 部署：

```
WEWE_RSS_URL=https://你的railway域名
WEWE_RSS_AUTH_CODE=123567
```

### 2. 测试连接

```bash
# 测试后端能否访问 WeWe-RSS
curl -H "Authorization: Bearer 123567" http://localhost:4000/feeds/all.json
```

### 3. 在应用中同步文章

后端已经有 `RSSService`，可以调用：

```python
from app.services.rss_service import RSSService

rss_service = RSSService()
await rss_service.sync_articles(account_id=1)
```

---

## 🎯 总结

1. ✅ 本地测试：用 Docker Compose
2. ✅ 生产部署：用 Railway/Zeabur
3. ✅ 添加账号：微信扫码登录微信读书
4. ✅ 订阅公众号：粘贴分享链接
5. ✅ 获取文章：通过 RSS/JSON/Atom 接口
6. ✅ 集成应用：配置环境变量，调用 RSSService

---

需要帮助？查看 [WEWE_RSS_SETUP.md](WEWE_RSS_SETUP.md) 获取更多信息。

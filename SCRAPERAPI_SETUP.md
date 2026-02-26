# 🚀 ScraperAPI 配置指南

## 📌 为什么需要 ScraperAPI？

微信文章有强大的反爬虫保护，直接抓取会失败。ScraperAPI 提供代理服务，可以绕过这些限制。

## 🎁 免费试用

- **免费额度**：5,000 次请求
- **无需信用卡**
- **足够测试和小规模使用**

---

## 📝 注册步骤

### 1. 访问 ScraperAPI 官网

```
https://www.scraperapi.com/
```

### 2. 注册账号

- 点击右上角 "Sign Up" 或 "Get Started Free"
- 可以用邮箱注册，或用 Google 账号登录
- 填写基本信息（邮箱、密码）

### 3. 验证邮箱

- 检查邮箱收件箱
- 点击验证链接

### 4. 获取 API Key

登录后，在 Dashboard 页面可以看到你的 API Key：

```
Your API Key: xxxxxxxxxxxxxxxxxxxxxxxx
```

复制这个 Key，后面要用。

---

## 🔧 配置到 Render

### 1. 登录 Render

访问：https://dashboard.render.com/

### 2. 找到你的后端服务

- 点击 "wechat-articles-backend" 服务
- 进入服务详情页

### 3. 添加环境变量

- 点击左侧 "Environment"
- 点击 "Add Environment Variable"
- 添加以下变量：

```
Key: SCRAPERAPI_KEY
Value: [粘贴你的 ScraperAPI Key]
```

### 4. 保存并重新部署

- 点击 "Save Changes"
- Render 会自动重新部署服务
- 等待部署完成（约 2-3 分钟）

---

## ✅ 测试抓取功能

### 1. 访问前端

```
https://wechat-articles.vercel.app
```

### 2. 点击"添加文章"

### 3. 粘贴测试链接

```
https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g
```

### 4. 点击"抓取文章"

如果配置正确，应该能成功抓取文章内容。

---

## 🔍 查看日志

如果抓取失败，可以在 Render 查看日志：

1. 进入服务详情页
2. 点击 "Logs" 标签
3. 查看错误信息

常见日志输出：

```
✅ 成功：
Scraping URL: https://mp.weixin.qq.com/s/...
Using ScraperAPI: True
ScraperAPI response: 200
Extracted:
   Title: 文章标题
   Content length: 1234 chars

❌ 失败：
ScraperAPI error: Invalid API key
或
ScraperAPI error: Request limit exceeded
```

---

## 💰 费用说明

### 免费套餐

- **5,000 次请求/月**
- 适合测试和小规模使用
- 每抓取一篇文章 = 1 次请求

### 付费套餐（可选）

如果免费额度用完，可以升级：

- **Hobby**: $49/月，100,000 次请求
- **Startup**: $149/月，1,000,000 次请求

对于个人使用，免费套餐通常足够。

---

## 🛠️ 故障排查

### 问题 1：抓取失败，提示 "Invalid API key"

**解决方案：**
- 检查 API Key 是否正确复制
- 确保没有多余的空格
- 在 Render 重新设置环境变量

### 问题 2：抓取失败，提示 "Request limit exceeded"

**解决方案：**
- 免费额度用完了
- 登录 ScraperAPI Dashboard 查看使用情况
- 考虑升级套餐或等待下月重置

### 问题 3：抓取成功但内容为空

**解决方案：**
- 微信文章可能需要登录才能查看
- 尝试其他公开文章
- 检查文章链接是否有效

### 问题 4：Render 环境变量不生效

**解决方案：**
- 确保点击了 "Save Changes"
- 等待服务重新部署完成
- 检查 Logs 确认新配置已加载

---

## 📊 监控使用情况

### 在 ScraperAPI Dashboard 查看：

1. 登录 https://www.scraperapi.com/
2. 进入 Dashboard
3. 查看：
   - 本月已使用请求数
   - 剩余请求数
   - 请求成功率

### 建议：

- 定期检查使用情况
- 避免重复抓取同一文章
- 考虑添加缓存机制

---

## 🎯 下一步

配置完成后，你可以：

1. ✅ 测试抓取功能
2. ✅ 添加多篇文章
3. ✅ 测试 AI 分析功能
4. ✅ 构建知识库

---

## 📞 需要帮助？

- **ScraperAPI 文档**: https://www.scraperapi.com/documentation/
- **项目 Issues**: https://github.com/j-lab-10404/wechat-articles/issues
- **邮件**: liujie@njfu.edu.cn

---

## 🔗 相关文档

- [环境变量完整清单](ENV_VARIABLES_CHECKLIST.md)
- [部署教程](docs/DEPLOY_TUTORIAL.md)
- [快速开始](docs/QUICK_START.md)

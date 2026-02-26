# 🔧 配置 Render MCP Server

通过 MCP 连接 Render，可以直接在 Kiro 中管理和检查后端部署。

---

## 📝 第一步：获取 Render API Key（2分钟）

1. **访问 Render Account Settings**
   - 打开：https://dashboard.render.com/u/settings
   - 或者：Render Dashboard → 右上角头像 → Account Settings

2. **创建 API Key**
   - 滚动到 "API Keys" 部分
   - 点击 "Create API Key"
   - 填写：
     - Name: `kiro-mcp`
     - 点击 "Create API Key"

3. **复制 API Key**
   - 复制生成的 API Key（只显示一次，请妥善保存）
   - 格式类似：`rnd_xxxxxxxxxxxxxxxxxxxxx`

---

## 🔌 第二步：配置 MCP（1分钟）

### 方法 1：通过 Kiro 界面配置（推荐）

1. 在 Kiro 中打开命令面板（Ctrl/Cmd + Shift + P）
2. 搜索并选择 "MCP: Edit Configuration"
3. 找到 `render` 配置部分
4. 将 `YOUR_RENDER_API_KEY_HERE` 替换为你的 API Key
5. 保存文件

### 方法 2：直接编辑配置文件

编辑 `wechat-articles/.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "render": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "RENDER_API_KEY",
        "render/mcp-server:latest"
      ],
      "env": {
        "RENDER_API_KEY": "rnd_你的API_Key"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

---

## ✅ 第三步：测试连接（1分钟）

配置完成后，在 Kiro 中尝试以下命令：

1. **设置工作空间**
   ```
   Set my Render workspace to [你的workspace名称]
   ```

2. **列出服务**
   ```
   List my Render services
   ```

3. **检查后端部署**
   ```
   Show me the status of wechat-articles-backend
   ```

4. **查看日志**
   ```
   Pull the most recent logs for wechat-articles-backend
   ```

---

## 🎯 常用命令

### 查看服务状态
```
What's the status of my wechat-articles-backend service?
```

### 查看日志
```
Show me the latest error logs for wechat-articles-backend
```

### 查看指标
```
What was the traffic like for my service today?
```

### 查看环境变量
```
List environment variables for wechat-articles-backend
```

### 修改环境变量
```
Add environment variable OPENAI_API_KEY=sk-xxx to wechat-articles-backend
```

---

## 🔒 安全提示

⚠️ **重要：Render API Key 权限很大**

- API Key 可以访问你账户下的所有工作空间和服务
- 不要分享或提交到 Git
- 定期轮换 API Key
- 目前 MCP Server 支持修改环境变量（可能有破坏性操作）

---

## 📚 支持的操作

### ✅ 可以做的事情

- 创建新服务（Web Service, Static Site, Cron Job）
- 创建数据库（Postgres, Redis）
- 查询服务状态和指标
- 查看日志
- 修改环境变量

### ❌ 暂不支持

- 删除服务
- 触发部署
- 修改扩展设置
- 创建镜像服务
- 设置 IP 白名单

---

## 🆘 故障排查

### MCP 连接失败？

1. **检查 Docker 是否运行**
   ```bash
   docker --version
   docker ps
   ```

2. **检查 API Key 是否正确**
   - 确认没有多余的空格
   - 确认以 `rnd_` 开头

3. **重启 MCP Server**
   - Kiro 命令面板 → "MCP: Restart Servers"

### 找不到服务？

1. **设置正确的工作空间**
   ```
   Set my Render workspace to [workspace名称]
   ```

2. **列出所有工作空间**
   ```
   List my Render workspaces
   ```

---

## 📖 更多信息

- [Render MCP Server 文档](https://render.com/docs/mcp-server)
- [Render MCP Server GitHub](https://github.com/render-examples/mcp-server)
- [MCP 协议规范](https://modelcontextprotocol.io/)

---

配置完成后，你就可以直接在 Kiro 中管理 Render 服务了！🎉

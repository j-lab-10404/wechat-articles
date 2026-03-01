"""Debug: 直接测试 WeWe-RSS API 返回的数据结构."""
import requests
import json

WEWE_RSS_URL = "https://wewe-rss-production-d5fc.up.railway.app"
TARGET_URL = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

print("1. 获取 all.json (limit=5)...")
resp = requests.get(f"{WEWE_RSS_URL}/feeds/all.json?limit=5", timeout=60)
data = resp.json()
items = data.get("items", [])
print(f"   获取到 {len(items)} 篇文章")

print(f"\n2. 检查 URL 匹配...")
for i, item in enumerate(items):
    url = item.get("url", "")
    title = item.get("title", "N/A")
    match = "✅ MATCH" if url == TARGET_URL else ""
    print(f"   [{i}] {title[:50]}")
    print(f"       URL: {url}")
    if match:
        print(f"       {match}")
        print(f"       content_text 长度: {len(item.get('content_text', ''))}")
        print(f"       content_html 长度: {len(item.get('content_html', ''))}")

# 3. 测试后端的 RSS 服务是否能连接到 WeWe-RSS
print(f"\n3. 测试后端环境变量...")
BACKEND = "https://wechat-articles-backend.onrender.com"
r = requests.get(f"{BACKEND}/", timeout=30)
root_data = r.json()
print(f"   wewe_rss: {root_data.get('wewe_rss', 'NOT SET')}")

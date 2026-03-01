"""测试从 WeWe-RSS 获取文章内容并提取纯文本."""
import requests
import json
import re
from bs4 import BeautifulSoup

WEWE_RSS_URL = "https://wewe-rss-production-d5fc.up.railway.app"

print("=" * 70)
print("测试 WeWe-RSS 文章内容提取")
print("=" * 70)

# 1. 获取文章列表（只取前5篇）
print("\n1. 获取文章列表...")
resp = requests.get(f"{WEWE_RSS_URL}/feeds/all.json?limit=5", timeout=60)
data = resp.json()
items = data.get("items", [])
print(f"   获取到 {len(items)} 篇文章")

if not items:
    print("   ❌ 没有文章，请先在 WeWe-RSS 添加订阅")
    exit(1)

# 2. 检查第一篇文章的内容
item = items[0]
print(f"\n2. 第一篇文章:")
print(f"   标题: {item.get('title', 'N/A')}")
print(f"   URL: {item.get('url', 'N/A')}")
print(f"   content_text 长度: {len(item.get('content_text', ''))}")
print(f"   content_html 长度: {len(item.get('content_html', ''))}")

# 3. 从 HTML 提取纯文本
html = item.get("content_html", "")
if html:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    
    content_div = soup.find(id="js_content") or soup.find(class_="rich_media_content")
    if content_div:
        text = content_div.get_text(separator="\n", strip=True)
        print(f"\n3. 从 #js_content 提取文本: {len(text)} 字")
    else:
        text = soup.get_text(separator="\n", strip=True)
        print(f"\n3. 从整个 HTML 提取文本: {len(text)} 字")
    
    text = re.sub(r'\n{3,}', '\n\n', text)
    print(f"   前 500 字:\n{'─' * 40}")
    print(text[:500])
    print(f"{'─' * 40}")
else:
    print("\n3. ❌ 没有 content_html")

# 4. 测试 URL 匹配
test_url = item.get("url", "")
print(f"\n4. 测试 URL 匹配:")
print(f"   目标 URL: {test_url}")

found = False
for a in items:
    if a["url"] == test_url:
        found = True
        break
print(f"   精确匹配: {'✅' if found else '❌'}")

print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)

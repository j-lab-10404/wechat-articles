"""调试 WeWe-RSS 文章 URL 匹配"""
import requests

target = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

resp = requests.get("https://wewe-rss-production-d5fc.up.railway.app/feeds/all.json?limit=50")
data = resp.json()

print(f"目标 URL: {target}")
print(f"文章总数: {len(data.get('items', []))}")
print()

found = False
for item in data.get("items", []):
    url = item.get("url", "")
    if "0LoxGei75oH" in url:
        print(f"✅ 找到匹配!")
        print(f"   WeWe URL: {url}")
        print(f"   目标 URL: {target}")
        print(f"   完全匹配: {url == target}")
        print(f"   有内容: {bool(item.get('content_html'))}")
        print(f"   内容长度: {len(item.get('content_html', ''))}")
        found = True
        break

if not found:
    print("❌ 未找到匹配")
    print("\n前 5 个 URL:")
    for item in data.get("items", [])[:5]:
        print(f"  {item.get('url', '')}")

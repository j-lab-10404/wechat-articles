"""查看 WeWe-RSS 中的文章"""
import requests

resp = requests.get("https://wewe-rss-production-d5fc.up.railway.app/feeds/all.json?limit=5")
data = resp.json()

for item in data.get("items", [])[:5]:
    print(item.get("title", "")[:60])
    print(f"  URL: {item.get('url', '')}")
    has_content = bool(item.get("content_html") or item.get("content_text"))
    print(f"  有内容: {has_content}")
    print()

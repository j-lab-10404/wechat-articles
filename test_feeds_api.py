"""测试 WeWe-RSS feeds API."""
import requests
import json

WEWE = "https://wewe-rss-production-d5fc.up.railway.app"

# 1. Get feeds list
print("1. GET /feeds")
r = requests.get(f"{WEWE}/feeds", timeout=30)
feeds = r.json()
print(f"   Type: {type(feeds).__name__}, count: {len(feeds)}")

for f in feeds:
    fid = f.get("id", "N/A")
    name = f.get("name", "N/A")
    print(f"   Feed: id={fid}, name={name}")

# 2. Get first feed's articles
if feeds:
    feed_id = feeds[0]["id"]
    print(f"\n2. GET /feeds/{feed_id}.json?limit=3")
    r = requests.get(f"{WEWE}/feeds/{feed_id}.json?limit=3", timeout=60)
    data = r.json()
    items = data.get("items", [])
    print(f"   Items: {len(items)}")
    for item in items:
        title = item.get("title", "N/A")
        url = item.get("url", "N/A")
        html_len = len(item.get("content_html", ""))
        text_len = len(item.get("content_text", ""))
        print(f"   - {title[:50]}")
        print(f"     url: {url}")
        print(f"     html: {html_len}, text: {text_len}")

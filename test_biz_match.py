"""Test __biz matching between article URL and feed mpUrl."""
import requests
from urllib.parse import urlparse, parse_qs

WEWE = "https://wewe-rss-production-d5fc.up.railway.app"
TARGET = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

# Check target URL biz
target_params = parse_qs(urlparse(TARGET).query)
target_biz = target_params.get("__biz", [""])[0]
print(f"Target URL: {TARGET}")
print(f"Target __biz: {repr(target_biz)}")
print(f"Target params: {target_params}")

# The short URL format (mp.weixin.qq.com/s/xxx) doesn't have __biz
# It's a redirect URL. The actual URL with __biz is different.
print("\nNote: Short URLs (mp.weixin.qq.com/s/xxx) don't contain __biz!")
print("WeWe-RSS stores the short URL format.")

# Check feeds
print("\nFeeds:")
r = requests.get(f"{WEWE}/feeds", timeout=10)
feeds = r.json()
for f in feeds:
    mp = f.get("mpUrl", "")
    biz = parse_qs(urlparse(mp).query).get("__biz", [""])[0] if mp else ""
    print(f"  {f['name']}: biz={repr(biz)}")
    print(f"    mpUrl: {mp[:80]}")

# Check if articles in feed have __biz in their URLs
print("\nArticle URLs in first feed:")
fid = feeds[0]["id"]
r = requests.get(f"{WEWE}/feeds/{fid}.json?limit=3", timeout=60)
data = r.json()
for item in data.get("items", [])[:3]:
    url = item.get("url", "")
    biz = parse_qs(urlparse(url).query).get("__biz", [""])[0]
    print(f"  {item.get('title', 'N/A')[:40]}")
    print(f"    URL: {url}")
    print(f"    __biz: {repr(biz)}")

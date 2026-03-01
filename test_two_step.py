"""Test the two-step flow: add article -> fetch content -> analyze."""
import requests
import json

BACKEND = "https://wechat-articles-backend.onrender.com"
TEST_URL = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

# Clean up
print("Cleaning up...")
r = requests.get(f"{BACKEND}/api/articles/", timeout=30)
for item in r.json().get("items", []):
    requests.delete(f"{BACKEND}/api/articles/{item['id']}", timeout=10)

# Step 1: Add article (no auto_analyze to keep it fast)
print(f"\nStep 1: Add article...")
resp = requests.post(
    f"{BACKEND}/api/articles/add",
    json={"url": TEST_URL, "auto_analyze": False},
    timeout=60,
)
print(f"  Status: {resp.status_code}")
data = resp.json()
print(f"  Response: {json.dumps(data, ensure_ascii=False)}")

if resp.status_code != 200 or not data.get("id"):
    print("FAILED at step 1")
    exit(1)

article_id = data["id"]
need_fetch = data.get("need_fetch", True)
print(f"  Article ID: {article_id}, need_fetch: {need_fetch}")

# Step 2: Fetch content (if needed)
if need_fetch:
    print(f"\nStep 2: Fetch content...")
    resp = requests.post(
        f"{BACKEND}/api/articles/{article_id}/fetch-content",
        timeout=180,
    )
    print(f"  Status: {resp.status_code}")
    if resp.status_code == 200:
        data2 = resp.json()
        print(f"  Title: {data2.get('title')}")
        print(f"  Content length: {data2.get('content_length')}")
    else:
        print(f"  Response: {resp.text[:200]}")
        print("  Content fetch failed, but article is saved")
else:
    print(f"\nStep 2: Content already fetched, title: {data.get('title')}")

# Step 3: Analyze
print(f"\nStep 3: AI Analyze...")
resp = requests.post(
    f"{BACKEND}/api/articles/{article_id}/analyze",
    timeout=120,
)
print(f"  Status: {resp.status_code}")
if resp.status_code == 200:
    data3 = resp.json()
    print(f"  Type: {data3.get('article_type')}")
    print(f"  Labels: {data3.get('labels')}")
    print(f"  Summary: {(data3.get('summary') or '')[:100]}...")
else:
    print(f"  Response: {resp.text[:200]}")

# Final check
print(f"\nFinal: Get article detail...")
resp = requests.get(f"{BACKEND}/api/articles/{article_id}", timeout=30)
detail = resp.json()
print(f"  Title: {detail.get('title')}")
print(f"  Type: {detail.get('article_type')}")
print(f"  Labels: {detail.get('labels')}")
print(f"  Papers: {len(detail.get('papers', []))}")
print(f"  Datasets: {len(detail.get('datasets', []))}")

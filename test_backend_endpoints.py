"""测试后端各端点."""
import requests
import json

BACKEND = "https://wechat-articles-backend.onrender.com"

print("=" * 60)
print("测试后端端点")
print("=" * 60)

# 1. Health check
print("\n1. Health check...")
try:
    r = requests.get(f"{BACKEND}/health", timeout=30)
    print(f"   {r.status_code}: {r.json()}")
except Exception as e:
    print(f"   ❌ {e}")

# 2. Papers endpoint
print("\n2. Papers endpoint...")
try:
    r = requests.get(f"{BACKEND}/api/papers/", timeout=30)
    print(f"   {r.status_code}: {json.dumps(r.json(), ensure_ascii=False)[:200]}")
except Exception as e:
    print(f"   ❌ {e}")

# 3. Datasets endpoint
print("\n3. Datasets endpoint...")
try:
    r = requests.get(f"{BACKEND}/api/datasets/", timeout=30)
    print(f"   {r.status_code}: {json.dumps(r.json(), ensure_ascii=False)[:200]}")
except Exception as e:
    print(f"   ❌ {e}")

# 4. Articles list
print("\n4. Articles list...")
try:
    r = requests.get(f"{BACKEND}/api/articles/", timeout=30)
    data = r.json()
    print(f"   {r.status_code}: total={data.get('total', 0)}")
except Exception as e:
    print(f"   ❌ {e}")

# 5. Labels
print("\n5. Labels...")
try:
    r = requests.get(f"{BACKEND}/api/articles/labels", timeout=30)
    print(f"   {r.status_code}: {json.dumps(r.json(), ensure_ascii=False)[:200]}")
except Exception as e:
    print(f"   ❌ {e}")

print("\n" + "=" * 60)

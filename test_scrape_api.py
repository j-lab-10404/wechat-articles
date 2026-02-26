"""测试后端抓取 API"""
import requests
import json

# 后端 URL
BACKEND_URL = "https://wechat-articles-backend.onrender.com"

# 测试文章 URL
test_url = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

print("=" * 60)
print("测试微信文章抓取 API")
print("=" * 60)

# 1. 测试健康检查
print("\n1️⃣ 测试健康检查...")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=10)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 测试抓取 API
print("\n2️⃣ 测试抓取文章...")
print(f"   文章 URL: {test_url}")

try:
    response = requests.post(
        f"{BACKEND_URL}/api/articles/scrape",
        json={"url": test_url},
        timeout=120  # 抓取可能需要较长时间
    )
    
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ 抓取成功!")
        print(f"   文章 ID: {data.get('id')}")
        print(f"   标题: {data.get('title')}")
        print(f"   作者: {data.get('author')}")
        print(f"   内容长度: {len(data.get('content_text', ''))} 字符")
        print(f"   封面图: {data.get('cover_image')}")
    else:
        print(f"   ❌ 抓取失败")
        print(f"   响应: {response.text}")
        
except requests.exceptions.Timeout:
    print(f"   ❌ 请求超时（120秒）")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

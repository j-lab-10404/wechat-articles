"""测试完整流程：添加文章 → AI 分析"""
import requests
import json

BACKEND = "https://wechat-articles-backend.onrender.com"

# 用 WeWe-RSS 里已有的文章
test_url = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

print("=" * 70)
print("测试完整流程：添加文章 + AI 分析")
print("=" * 70)

print(f"\n📝 文章 URL: {test_url}")
print("🚀 发送请求...")

resp = requests.post(
    f"{BACKEND}/api/articles/add",
    json={"url": test_url, "auto_analyze": True},
    timeout=120,
)

print(f"\n📊 状态码: {resp.status_code}")
data = resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))

if resp.status_code == 200 and data.get("id"):
    article_id = data["id"]
    print(f"\n✅ 文章已添加，ID: {article_id}")
    
    # 获取详情
    detail = requests.get(f"{BACKEND}/api/articles/{article_id}", timeout=30).json()
    print(f"\n📋 文章详情:")
    print(f"   标题: {detail.get('title')}")
    print(f"   类型: {detail.get('article_type')}")
    print(f"   标签: {detail.get('labels')}")
    print(f"   摘要: {(detail.get('summary') or '')[:100]}...")
    print(f"   论文数: {len(detail.get('papers', []))}")
    print(f"   数据集数: {len(detail.get('datasets', []))}")
else:
    print(f"\n❌ 添加失败: {data}")

print("\n" + "=" * 70)

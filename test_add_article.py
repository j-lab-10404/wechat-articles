"""测试完整流程：添加文章 → 获取内容 → AI 分析."""
import requests
import json

BACKEND = "https://wechat-articles-backend.onrender.com"

# 先删除之前的测试文章（如果有）
print("清理旧数据...")
r = requests.get(f"{BACKEND}/api/articles/", timeout=30)
for item in r.json().get("items", []):
    requests.delete(f"{BACKEND}/api/articles/{item['id']}", timeout=10)
    print(f"  删除: {item['title'][:40]}")

# 用 WeWe-RSS 里已有的文章
test_url = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"

print(f"\n{'=' * 60}")
print(f"添加文章: {test_url}")
print(f"{'=' * 60}")

resp = requests.post(
    f"{BACKEND}/api/articles/add",
    json={"url": test_url, "auto_analyze": True},
    timeout=180,  # AI 分析可能需要较长时间
)

print(f"\n状态码: {resp.status_code}")
data = resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))

if resp.status_code == 200 and data.get("id"):
    article_id = data["id"]
    print(f"\n✅ 文章已添加，ID: {article_id}")
    print(f"   内容长度: {data.get('content_length', 0)} 字")
    print(f"   分析状态: {data.get('analysis_status')}")
    
    if data.get("analysis_status") == "completed":
        print(f"   类型: {data.get('article_type')}")
        print(f"   标签: {data.get('labels')}")
        print(f"   摘要: {(data.get('summary') or '')[:100]}...")
        print(f"   论文数: {data.get('papers_count', 0)}")
        print(f"   数据集数: {data.get('datasets_count', 0)}")
    
    # 获取详情
    print(f"\n获取文章详情...")
    detail = requests.get(f"{BACKEND}/api/articles/{article_id}", timeout=30).json()
    print(f"   论文: {len(detail.get('papers', []))}")
    print(f"   数据集: {len(detail.get('datasets', []))}")
    
    if detail.get("papers"):
        for p in detail["papers"]:
            print(f"   📄 {p.get('title', 'N/A')}")
            if p.get("doi"):
                print(f"      DOI: {p['doi']}")
            if p.get("arxiv_id"):
                print(f"      arXiv: {p['arxiv_id']}")
else:
    print(f"\n❌ 添加失败")

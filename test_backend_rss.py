"""测试后端是否能正确从 WeWe-RSS 获取内容.
通过调用后端的 add 端点并查看日志来诊断问题。
"""
import requests
import json

BACKEND = "https://wechat-articles-backend.onrender.com"

# 先清理
print("清理旧数据...")
r = requests.get(f"{BACKEND}/api/articles/", timeout=30)
for item in r.json().get("items", []):
    requests.delete(f"{BACKEND}/api/articles/{item['id']}", timeout=10)

# 测试 - 不开启 AI 分析，只测试内容获取
test_url = "https://mp.weixin.qq.com/s/0LoxGei75oH_wxGSDxzPAw"
print(f"\n添加文章 (auto_analyze=False): {test_url}")

resp = requests.post(
    f"{BACKEND}/api/articles/add",
    json={"url": test_url, "auto_analyze": False},
    timeout=120,
)

print(f"状态码: {resp.status_code}")
data = resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))

if data.get("id"):
    # 获取详情看看内容
    detail = requests.get(f"{BACKEND}/api/articles/{data['id']}", timeout=30).json()
    content_len = len(detail.get("content", "") or "")
    text_len = len(detail.get("content_text", "") or "")
    print(f"\n详情:")
    print(f"  title: {detail.get('title')}")
    print(f"  content (HTML) 长度: {content_len}")
    print(f"  content_text 长度: {text_len}")
    if text_len > 0:
        print(f"  content_text 前200字: {detail['content_text'][:200]}")

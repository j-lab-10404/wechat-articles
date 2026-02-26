#!/usr/bin/env python3
"""
测试微信文章抓取功能
"""
import requests
import json

# 配置
BACKEND_URL = "https://wechat-articles-backend.onrender.com"
API_BASE = f"{BACKEND_URL}/api"
TEST_URL = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

def test_health():
    """测试健康检查"""
    print("\n🏥 测试健康检查...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"   响应: {response.json()}")
            return True
        return False
    except Exception as e:
        print(f"   错误: {str(e)}")
        return False

def test_scrape():
    """测试抓取接口"""
    print("=" * 60)
    print("🧪 测试微信文章抓取")
    print("=" * 60)
    
    # 先测试健康检查
    if not test_health():
        print("\n❌ 后端服务不可用")
        return
    
    print(f"\n📝 测试文章: {TEST_URL}")
    
    try:
        # 调用抓取接口
        print("\n⏳ 正在抓取文章...")
        response = requests.post(
            f"{API_BASE}/articles/scrape",
            json={
                "url": TEST_URL,
                "auto_analyze": False  # 先不分析，只测试抓取
            },
            timeout=60
        )
        
        print(f"\n📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ 抓取成功！")
            print(f"\n文章信息:")
            print(f"  ID: {data.get('id')}")
            print(f"  标题: {data.get('title')}")
            print(f"  作者: {data.get('author')}")
            print(f"  分类: {data.get('category')}")
            print(f"  URL: {data.get('url')}")
            print(f"\n内容预览:")
            content_text = data.get('content_text', '')
            print(f"  {content_text[:200]}...")
        else:
            print(f"\n❌ 抓取失败")
            print(f"\n完整响应:")
            print(f"  状态码: {response.status_code}")
            print(f"  内容类型: {response.headers.get('content-type')}")
            print(f"  响应体:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, ensure_ascii=False, indent=2))
            except:
                print(response.text[:1000])  # 只打印前1000字符
                
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时（可能是服务正在休眠，请重试）")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scrape()

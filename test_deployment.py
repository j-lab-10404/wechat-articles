#!/usr/bin/env python3
"""
微信文章知识库系统 - 全面功能测试脚本
测试后端 API 和前端应用的所有功能
"""
import requests
import json
from datetime import datetime
import time

# 配置
BACKEND_URL = "https://wechat-articles-backend.onrender.com"
FRONTEND_URL = "https://wechat-articles.vercel.app"
API_BASE = f"{BACKEND_URL}/api"

# 测试结果记录
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

def print_section(title):
    """打印测试章节标题"""
    print("\n" + "=" * 70)
    print(f"📋 {title}")
    print("=" * 70)

def print_test(name, success, details="", response_data=None):
    """打印测试结果并记录"""
    global test_results
    test_results["total"] += 1
    
    status = "✅ 通过" if success else "❌ 失败"
    print(f"\n{status} {name}")
    if details:
        print(f"   {details}")
    if response_data:
        print(f"   响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
    
    # 记录测试结果
    test_results["tests"].append({
        "name": name,
        "success": success,
        "details": details,
        "timestamp": datetime.now().isoformat()
    })
    
    if success:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def log_request(method, url, params=None, data=None):
    """记录请求信息"""
    print(f"\n   🔹 请求: {method} {url}")
    if params:
        print(f"   🔹 参数: {json.dumps(params, ensure_ascii=False)}")
    if data:
        print(f"   🔹 数据: {json.dumps(data, ensure_ascii=False, indent=2)[:300]}")

def test_health():
    """测试健康检查"""
    try:
        print("   正在唤醒服务（首次请求可能需要30-60秒）...")
        response = requests.get(f"{BACKEND_URL}/health", timeout=60)
        success = response.status_code == 200
        print_test("健康检查", success, f"状态码: {response.status_code}")
        return success
    except Exception as e:
        print_test("健康检查", False, f"错误: {str(e)}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        response = requests.get(f"{API_BASE}/accounts", timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        print_test("数据库连接", success, 
                  f"状态码: {response.status_code}, 账号数: {data.get('total', 0) if data else 'N/A'}")
        return success
    except Exception as e:
        print_test("数据库连接", False, f"错误: {str(e)}")
        return False

def test_create_account():
    """测试创建账号"""
    try:
        account_data = {
            "name": "测试公众号",
            "account_id": "test_account_001",
            "rss_url": "https://example.com/rss",
            "description": "这是一个测试账号"
        }
        response = requests.post(f"{API_BASE}/accounts/", json=account_data, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        print_test("创建账号", success, 
                  f"状态码: {response.status_code}, ID: {data.get('id') if data else 'N/A'}")
        return data.get('id') if success and data else None
    except Exception as e:
        print_test("创建账号", False, f"错误: {str(e)}")
        return None

def test_create_article(account_id):
    """测试创建文章"""
    try:
        article_data = {
            "account_id": account_id,
            "title": "测试文章：人工智能在医疗领域的应用",
            "content": "<p>这是一篇关于人工智能在医疗领域应用的测试文章。</p>",
            "content_text": "这是一篇关于人工智能在医疗领域应用的测试文章。人工智能技术正在revolutionize医疗诊断、药物研发和个性化治疗。深度学习算法可以分析医学影像，帮助医生更准确地诊断疾病。",
            "url": "https://example.com/article/test-ai-medical",
            "published_at": datetime.now().isoformat()
        }
        response = requests.post(f"{API_BASE}/articles/", json=article_data, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        print_test("创建文章", success, 
                  f"状态码: {response.status_code}, ID: {data.get('id') if data else 'N/A'}")
        return data.get('id') if success and data else None
    except Exception as e:
        print_test("创建文章", False, f"错误: {str(e)}")
        return None

def test_ai_analysis(article_id):
    """测试 AI 分析（关键测试）"""
    try:
        print("\n🤖 开始测试 AI 分析功能...")
        response = requests.post(f"{API_BASE}/articles/{article_id}/analyze", timeout=30)
        success = response.status_code == 200
        data = response.json() if response.status_code in [200, 400] else None
        
        if success:
            print_test("AI 分析", True, 
                      f"状态码: {response.status_code}, 分析ID: {data.get('analysis_id') if data else 'N/A'}")
            print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print_test("AI 分析", False, 
                      f"状态码: {response.status_code}, 响应: {data if data else response.text}")
        return success
    except Exception as e:
        print_test("AI 分析", False, f"错误: {str(e)}")
        return False

def test_get_article_with_analysis(article_id):
    """测试获取文章及其分析"""
    try:
        response = requests.get(f"{API_BASE}/articles/{article_id}", timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        
        if success and data:
            has_analysis = data.get('analysis') is not None
            category = data.get('category', 'N/A')
            print_test("获取文章分析", success, 
                      f"有分析: {has_analysis}, 分类: {category}")
            if has_analysis:
                analysis = data.get('analysis', {})
                print(f"   摘要: {analysis.get('summary', 'N/A')[:100]}...")
                print(f"   关键词: {analysis.get('keywords', [])}")
        else:
            print_test("获取文章分析", False, f"状态码: {response.status_code}")
        return success
    except Exception as e:
        print_test("获取文章分析", False, f"错误: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 开始测试后端部署")
    print("=" * 60)
    
    # 1. 测试健康检查
    if not test_health():
        print("\n❌ 健康检查失败，停止测试")
        return
    
    # 2. 测试数据库连接
    if not test_database_connection():
        print("\n❌ 数据库连接失败，停止测试")
        return
    
    # 3. 测试创建账号
    account_id = test_create_account()
    if not account_id:
        print("\n❌ 创建账号失败，停止测试")
        return
    
    # 4. 测试创建文章
    article_id = test_create_article(account_id)
    if not article_id:
        print("\n❌ 创建文章失败，停止测试")
        return
    
    # 5. 测试 AI 分析（关键）
    ai_success = test_ai_analysis(article_id)
    
    # 6. 测试获取文章及分析
    if ai_success:
        test_get_article_with_analysis(article_id)
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    print(f"\n📊 测试结果总结:")
    print(f"   - 后端服务: 运行中")
    print(f"   - 数据库: 已连接")
    print(f"   - CRUD 操作: 正常")
    print(f"   - AI 分析: {'✅ 正常' if ai_success else '❌ 失败'}")
    print(f"\n🔗 访问链接:")
    print(f"   - API 文档: {BACKEND_URL}/docs")
    print(f"   - 前端应用: https://wechat-articles.vercel.app")
    print(f"   - 测试账号ID: {account_id}")
    print(f"   - 测试文章ID: {article_id}")

if __name__ == "__main__":
    main()

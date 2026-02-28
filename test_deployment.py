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

# ============================================================================
# 1. 后端健康检查测试
# ============================================================================

def test_health():
    """测试后端健康检查"""
    try:
        url = f"{BACKEND_URL}/health"
        log_request("GET", url)
        print("   ⏳ 正在唤醒服务（首次请求可能需要30-60秒）...")
        
        response = requests.get(url, timeout=90)
        success = response.status_code == 200
        data = response.json() if success else None
        
        print_test(
            "后端健康检查 (/health)", 
            success, 
            f"状态码: {response.status_code}",
            data
        )
        return success, data
    except Exception as e:
        print_test("后端健康检查 (/health)", False, f"错误: {str(e)}")
        return False, None

# ============================================================================
# 2. 公众号 CRUD 操作测试
# ============================================================================

def test_get_accounts():
    """测试获取公众号列表"""
    try:
        url = f"{API_BASE}/accounts"
        log_request("GET", url)
        
        response = requests.get(url, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        
        print_test(
            "获取公众号列表 (GET /api/accounts)", 
            success, 
            f"状态码: {response.status_code}, 总数: {data.get('total', 0) if data else 'N/A'}",
            data
        )
        return success, data
    except Exception as e:
        print_test("获取公众号列表", False, f"错误: {str(e)}")
        return False, None

def test_create_account():
    """测试创建公众号"""
    try:
        account_data = {
            "name": f"测试公众号_{int(time.time())}",
            "account_id": f"test_account_{int(time.time())}",
            "rss_url": "https://example.com/rss",
            "description": "这是一个用于全面测试的公众号账号"
        }
        
        url = f"{API_BASE}/accounts/"
        log_request("POST", url, data=account_data)
        
        response = requests.post(url, json=account_data, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        
        print_test(
            "创建公众号 (POST /api/accounts/)", 
            success, 
            f"状态码: {response.status_code}, ID: {data.get('id') if data else 'N/A'}",
            data
        )
        return success, data
    except Exception as e:
        print_test("创建公众号", False, f"错误: {str(e)}")
        return False, None

def test_update_account(account_id):
    """测试更新公众号信息"""
    try:
        update_data = {
            "description": f"更新后的描述 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        url = f"{API_BASE}/accounts/{account_id}"
        log_request("PUT", url, data=update_data)
        
        response = requests.put(url, json=update_data, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        
        print_test(
            "更新公众号信息 (PUT /api/accounts/{id})", 
            success, 
            f"状态码: {response.status_code}",
            data
        )
        return success, data
    except Exception as e:
        print_test("更新公众号信息", False, f"错误: {str(e)}")
        return False, None

def test_get_account_detail(account_id):
    """测试获取公众号详情"""
    try:
        url = f"{API_BASE}/accounts/{account_id}"
        log_request("GET", url)
        
        response = requests.get(url, timeout=10)
        success = response.status_code == 200
        data = response.json() if success else None
        
        print_test(
            "获取公众号详情 (GET /api/accounts/{id})", 
            success, 
            f"状态码: {response.status_code}",
            data
        )
        return success, data
    except Exception as e:
        print_test("获取公众号详情", False, f"错误: {str(e)}")
        return False, None

# ============================================================================
# 3. 文章 CRUD 操作测试
# ============================================================================

def test_create_article(account_id):
    """测试创建文章（包含中文内容）"""
    try:
        article_data = {
            "account_id": account_id,
            "title": "测试文章：人工智能在医疗健康领域的创新应用",
            "content": """
            <h1>人工智能在医疗健康领域的创新应用</h1>
            <p>人工智能（AI）技术正在深刻改变医疗健康行业的面貌。从疾病诊断到药物研发，从个性化治疗到健康管理，AI的应用无处不在。</p>
            <h2>主要应用领域</h2>
            <ul>
                <li><strong>医学影像分析：</strong>深度学习算法可以快速准确地分析X光、CT、MRI等医学影像，辅助医生诊断。</li>
                <li><strong>药物研发：</strong>AI可以加速新药发现过程，预测药物分子的有效性和安全性。</li>
                <li><strong>个性化医疗：</strong>基于患者的基因组数据和病史，AI可以推荐最适合的治疗方案。</li>
                <li><strong>健康监测：</strong>智能穿戴设备结合AI算法，实现24小时健康监测和预警。</li>
            </ul>
            <h2>未来展望</h2>
            <p>随着技术的不断进步，AI将在精准医疗、远程医疗、医疗机器人等领域发挥更大作用，为人类健康事业做出更大贡献。</p>
            """,
            "content_text": """
            人工智能在医疗健康领域的创新应用
            
            人工智能（AI）技术正在深刻改变医疗健康行业的面貌。从疾病诊断到药物研发，从个性化治疗到健康管理，AI的应用无处不在。
            
            主要应用领域：
            1. 医学影像分析：深度学习算法可以快速准确地分析X光、CT、MRI等医学影像，辅助医生诊断。
            2. 药物研发：AI可以加速新药发现过程，预测药物分子的有效性和安全性。
            3. 个性化医疗：基于患者的基因组数据和病史，AI可以推荐最适合的治疗方案。
            4. 健康监测：智能穿戴设备结合AI算法，实现24小时健康监测和预警。
            
            未来展望：
            随着技术的不断进步，AI将在精准医疗、远程医疗、医疗机器人等领域发挥更大作用，为人类健康事业做出更大贡献。
            """,
            "url": f"https://example.com/article/ai-healthcare-{int(time.time())}",
            "published_at": datetime.now().isoformat()
        }
        
        url = f"{API_BASE}/articles/"
        log_request("POST", url, data=article_data)
        
        response = requests.post(url, json=article_dat

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

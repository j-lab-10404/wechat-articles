"""测试 WeWe-RSS 服务"""
import requests
import json
import os

# WeWe-RSS 配置
WEWE_RSS_URL = os.getenv('WEWE_RSS_URL', 'http://localhost:4000')
AUTH_CODE = os.getenv('WEWE_RSS_AUTH_CODE', '123567')

print("=" * 70)
print("测试 WeWe-RSS 服务")
print("=" * 70)
print(f"\n🌐 WeWe-RSS URL: {WEWE_RSS_URL}")
print(f"🔑 Auth Code: {AUTH_CODE}")

# 准备请求头
headers = {}
if AUTH_CODE:
    headers['Authorization'] = f'Bearer {AUTH_CODE}'

# 1. 测试健康检查
print("\n" + "=" * 70)
print("1️⃣ 测试服务是否运行")
print("=" * 70)

try:
    response = requests.get(f"{WEWE_RSS_URL}/", timeout=10)
    print(f"✅ 状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ WeWe-RSS 服务正常运行")
    else:
        print(f"⚠️  返回状态码: {response.status_code}")
except Exception as e:
    print(f"❌ 无法连接到 WeWe-RSS: {e}")
    print("\n💡 提示:")
    print("   1. 确保 WeWe-RSS 已启动")
    print("   2. 检查 URL 是否正确")
    print("   3. 如果是本地部署，运行: docker-compose -f docker-compose.wewe-rss.yml up -d")
    exit(1)

# 2. 测试获取所有文章（JSON 格式）
print("\n" + "=" * 70)
print("2️⃣ 测试获取文章列表（JSON）")
print("=" * 70)

try:
    response = requests.get(
        f"{WEWE_RSS_URL}/feeds/all.json",
        headers=headers,
        timeout=10
    )
    
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        print(f"✅ 成功获取文章")
        print(f"📝 文章数量: {len(items)}")
        
        if len(items) > 0:
            print(f"\n📄 最新 3 篇文章:")
            for i, item in enumerate(items[:3], 1):
                print(f"\n   {i}. {item.get('title', '无标题')}")
                print(f"      🔗 链接: {item.get('url', 'N/A')}")
                print(f"      📅 发布: {item.get('date_published', 'N/A')}")
                print(f"      ✍️  作者: {item.get('author', {}).get('name', 'N/A')}")
        else:
            print("\n⚠️  暂无文章")
            print("💡 提示: 请先在 WeWe-RSS 管理界面添加公众号订阅")
    else:
        print(f"❌ 获取失败: {response.status_code}")
        print(f"📄 响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 3. 测试获取 RSS 格式
print("\n" + "=" * 70)
print("3️⃣ 测试获取文章列表（RSS）")
print("=" * 70)

try:
    response = requests.get(
        f"{WEWE_RSS_URL}/feeds/all.rss",
        headers=headers,
        timeout=10
    )
    
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ RSS 格式正常")
        print(f"📏 内容长度: {len(response.text)} 字符")
        
        # 检查是否包含文章
        if '<item>' in response.text:
            count = response.text.count('<item>')
            print(f"📝 包含 {count} 篇文章")
        else:
            print("⚠️  RSS 中暂无文章")
    else:
        print(f"❌ 获取失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 4. 测试获取 Atom 格式
print("\n" + "=" * 70)
print("4️⃣ 测试获取文章列表（Atom）")
print("=" * 70)

try:
    response = requests.get(
        f"{WEWE_RSS_URL}/feeds/all.atom",
        headers=headers,
        timeout=10
    )
    
    print(f"📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"✅ Atom 格式正常")
        print(f"📏 内容长度: {len(response.text)} 字符")
        
        # 检查是否包含文章
        if '<entry>' in response.text:
            count = response.text.count('<entry>')
            print(f"📝 包含 {count} 篇文章")
        else:
            print("⚠️  Atom 中暂无文章")
    else:
        print(f"❌ 获取失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 总结
print("\n" + "=" * 70)
print("✅ 测试完成")
print("=" * 70)

print("\n📋 下一步:")
print("   1. 访问 WeWe-RSS 管理界面: " + WEWE_RSS_URL)
print("   2. 添加微信读书账号（扫码登录）")
print("   3. 订阅公众号（粘贴公众号分享链接）")
print("   4. 等待文章同步完成")
print("   5. 再次运行此脚本查看文章")

print("\n🔗 RSS 地址:")
print(f"   JSON: {WEWE_RSS_URL}/feeds/all.json")
print(f"   RSS:  {WEWE_RSS_URL}/feeds/all.rss")
print(f"   Atom: {WEWE_RSS_URL}/feeds/all.atom")

print("\n" + "=" * 70)

"""直接测试 ScraperAPI"""
import requests
import os

# 从环境变量获取 API Key（如果有）
api_key = os.getenv('SCRAPERAPI_KEY', '')

if not api_key:
    print("❌ 请设置 SCRAPERAPI_KEY 环境变量")
    print("   例如: export SCRAPERAPI_KEY=your_key_here")
    exit(1)

print("=" * 60)
print("直接测试 ScraperAPI")
print("=" * 60)

# 测试 URL
test_url = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

print(f"\n🔑 API Key: {api_key[:10]}...")
print(f"🌐 测试 URL: {test_url}")

try:
    print("\n📡 调用 ScraperAPI...")
    
    response = requests.get(
        'http://api.scraperapi.com',
        params={
            'api_key': api_key,
            'url': test_url,
            'render': 'true',
            'country_code': 'cn'
        },
        timeout=60
    )
    
    print(f"📊 状态码: {response.status_code}")
    print(f"📏 响应长度: {len(response.text)} bytes")
    
    if response.status_code == 200:
        print("✅ ScraperAPI 调用成功!")
        
        # 检查内容
        if '微信' in response.text or 'weixin' in response.text.lower():
            print("✅ 响应包含微信相关内容")
        
        # 保存到文件查看
        with open('scraperapi_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("💾 响应已保存到 scraperapi_response.html")
        
        # 显示前 500 字符
        print(f"\n📄 响应预览（前 500 字符）:")
        print("-" * 60)
        print(response.text[:500])
        print("-" * 60)
    else:
        print(f"❌ ScraperAPI 返回错误: {response.status_code}")
        print(f"📄 错误信息: {response.text}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时（60秒）")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 60)

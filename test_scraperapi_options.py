"""测试不同的 ScraperAPI 参数组合"""
import requests
from bs4 import BeautifulSoup

api_key = "011b933bb6a5ed7b3b268630b9aa62fe"
test_url = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

def test_scrape(params_desc, params):
    """测试一组参数"""
    print(f"\n{'='*70}")
    print(f"测试: {params_desc}")
    print(f"参数: {params}")
    print('='*70)
    
    try:
        response = requests.get(
            'http://api.scraperapi.com',
            params={**params, 'api_key': api_key, 'url': test_url},
            timeout=90
        )
        
        print(f"📊 状态码: {response.status_code}")
        print(f"📏 响应长度: {len(response.text)} bytes")
        
        # 检查是否是验证页面
        if '环境异常' in response.text or '验证' in response.text:
            print("❌ 返回验证页面")
            return False
        
        # 用 BeautifulSoup 解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找标题
        title = soup.find('h1', class_='rich_media_title')
        if title:
            print(f"✅ 标题: {title.get_text().strip()}")
        
        # 查找内容
        content = soup.find('div', id='js_content')
        if content:
            text = content.get_text().strip()
            print(f"✅ 内容长度: {len(text)} 字符")
            if len(text) > 0:
                print(f"📄 内容预览: {text[:100]}...")
                return True
        
        print("❌ 未找到内容")
        return False
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

print("="*70)
print("测试不同的 ScraperAPI 参数组合")
print("="*70)

# 测试不同的参数组合
test_cases = [
    ("默认参数（无 render）", {}),
    ("启用 JS 渲染", {'render': 'true'}),
    ("启用 JS 渲染 + 中国代理", {'render': 'true', 'country_code': 'cn'}),
    ("启用 JS 渲染 + 美国代理", {'render': 'true', 'country_code': 'us'}),
    ("Premium 代理", {'premium': 'true'}),
    ("Premium + JS 渲染", {'premium': 'true', 'render': 'true'}),
    ("Premium + JS 渲染 + 中国", {'premium': 'true', 'render': 'true', 'country_code': 'cn'}),
    ("Ultra Premium", {'ultra_premium': 'true'}),
    ("Ultra Premium + 渲染", {'ultra_premium': 'true', 'render': 'true'}),
]

success_count = 0
for desc, params in test_cases:
    if test_scrape(desc, params):
        success_count += 1
        print("✅ 成功!")
    else:
        print("❌ 失败")

print(f"\n{'='*70}")
print(f"测试完成: {success_count}/{len(test_cases)} 成功")
print('='*70)

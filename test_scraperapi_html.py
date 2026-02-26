"""测试 ScraperAPI 返回的 HTML 内容"""
import requests
import os
from bs4 import BeautifulSoup

api_key = "011b933bb6a5ed7b3b268630b9aa62fe"
test_url = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

print("=" * 70)
print("测试 ScraperAPI 返回的 HTML")
print("=" * 70)

print(f"\n🌐 调用 ScraperAPI...")

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

# 保存 HTML
with open('wechat_article.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("💾 HTML 已保存到 wechat_article.html")

# 用 BeautifulSoup 解析
print("\n🔍 用 BeautifulSoup 解析...")
soup = BeautifulSoup(response.text, 'html.parser')

# 查找标题
title = soup.find('h1', class_='rich_media_title')
if title:
    print(f"✅ 标题: {title.get_text().strip()}")
else:
    print("❌ 未找到标题")

# 查找作者
author = soup.find('a', class_='rich_media_meta_nickname')
if author:
    print(f"✅ 作者: {author.get_text().strip()}")
else:
    print("❌ 未找到作者")

# 查找内容
content = soup.find('div', id='js_content')
if content:
    text = content.get_text().strip()
    print(f"✅ 内容长度: {len(text)} 字符")
    print(f"\n📄 内容预览（前 300 字符）:")
    print("-" * 70)
    print(text[:300])
    print("-" * 70)
else:
    print("❌ 未找到内容")

print("\n" + "=" * 70)

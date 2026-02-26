"""本地测试 WeChatScraper"""
import sys
import os

# 先设置环境变量，再导入模块
SCRAPERAPI_KEY = os.getenv('SCRAPERAPI_KEY', '')

if not SCRAPERAPI_KEY:
    print("⚠️  未设置 SCRAPERAPI_KEY 环境变量")
    print("   将尝试直接抓取（可能失败）")
    print()

# 设置环境变量供 config 使用
os.environ['SCRAPERAPI_KEY'] = SCRAPERAPI_KEY
os.environ['DATABASE_URL'] = 'postgresql://dummy'  # 占位符
os.environ['SECRET_KEY'] = 'dummy'  # 占位符
os.environ['OPENAI_API_KEY'] = 'dummy'  # 占位符

# 添加 backend 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.wechat_scraper import WeChatScraper

print("=" * 70)
print("本地测试 WeChatScraper")
print("=" * 70)

# 测试 URL
test_url = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

print(f"\n📝 测试 URL: {test_url}")
print(f"🔑 ScraperAPI Key: {'已设置 (' + SCRAPERAPI_KEY[:10] + '...)' if SCRAPERAPI_KEY else '未设置'}")
print()

try:
    # 创建 scraper
    print("🔧 创建 WeChatScraper 实例...")
    scraper = WeChatScraper()
    
    print(f"   ✅ Scraper 创建成功")
    print(f"   🔑 API Key 已配置: {scraper.use_scraperapi}")
    print()
    
    # 抓取文章
    print("🚀 开始抓取文章...")
    print("-" * 70)
    
    article_data = scraper.scrape_article(test_url)
    
    print("-" * 70)
    
    if article_data:
        print("\n✅ 抓取成功!")
        print()
        print("📊 文章信息:")
        print(f"   标题: {article_data.get('title')}")
        print(f"   作者: {article_data.get('author', '未知')}")
        print(f"   公众号: {article_data.get('account_name', '未知')}")
        print(f"   发布时间: {article_data.get('published_at')}")
        print(f"   封面图: {article_data.get('cover_image', '无')}")
        print(f"   内容长度: {len(article_data.get('content_text', ''))} 字符")
        print(f"   HTML 长度: {len(article_data.get('content', ''))} 字符")
        print()
        
        # 显示内容预览
        content_text = article_data.get('content_text', '')
        if content_text:
            print("📄 内容预览（前 200 字符）:")
            print("-" * 70)
            print(content_text[:200])
            print("-" * 70)
        else:
            print("⚠️  警告: 内容为空")
    else:
        print("\n❌ 抓取失败: 返回 None")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print(f"❌ 错误类型: {type(e).__name__}")
    
    import traceback
    print("\n📋 详细错误信息:")
    print("-" * 70)
    traceback.print_exc()
    print("-" * 70)

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)

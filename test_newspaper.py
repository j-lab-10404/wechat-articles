#!/usr/bin/env python3
"""
本地测试 newspaper3k 是否能抓取微信文章
"""
from newspaper import Article

TEST_URL = "https://mp.weixin.qq.com/s/jrPxvFgzfN8_FhjYotG40g"

print("=" * 60)
print("🧪 本地测试 newspaper3k")
print("=" * 60)

print(f"\n📝 测试文章: {TEST_URL}")

try:
    print("\n⏳ 正在抓取...")
    
    # 创建 Article 对象
    article = Article(TEST_URL, language='zh')
    
    # 下载
    print("   下载中...")
    article.download()
    print("   ✅ 下载完成")
    
    # 解析
    print("   解析中...")
    article.parse()
    print("   ✅ 解析完成")
    
    # 显示结果
    print(f"\n📄 提取结果:")
    print(f"   标题: {article.title}")
    print(f"   作者: {article.authors}")
    print(f"   发布时间: {article.publish_date}")
    print(f"   顶部图片: {article.top_image}")
    print(f"   内容长度: {len(article.text)} 字符")
    print(f"\n   内容预览:")
    print(f"   {article.text[:300]}...")
    
    print("\n✅ 测试成功！")
    
except Exception as e:
    print(f"\n❌ 测试失败: {str(e)}")
    import traceback
    traceback.print_exc()

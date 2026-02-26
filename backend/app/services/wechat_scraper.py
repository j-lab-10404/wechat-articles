"""WeChat article scraper service."""
from newspaper import Article
from typing import Dict, Optional
from datetime import datetime


class WeChatScraper:
    """Scrape WeChat articles using newspaper3k."""
    
    def __init__(self):
        pass
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape article from WeChat URL using newspaper3k.
        
        Args:
            url: WeChat article URL
            
        Returns:
            Dict with article data or None if failed
        """
        try:
            print(f"Scraping URL: {url}")
            
            # Create Article object
            article = Article(url, language='zh')
            
            # Download and parse
            article.download()
            article.parse()
            
            # Try NLP for keywords and summary
            try:
                article.nlp()
            except Exception as e:
                print(f"NLP processing failed: {str(e)}")
            
            # Extract data
            article_data = {
                'url': url,
                'title': article.title or "未知标题",
                'author': ', '.join(article.authors) if article.authors else None,
                'account_name': None,  # newspaper3k doesn't extract this
                'content': article.html or "",
                'content_text': article.text or "",
                'published_at': article.publish_date or datetime.now(),
                'cover_image': article.top_image or None,
            }
            
            print(f"✅ Successfully extracted:")
            print(f"   Title: {article_data['title']}")
            print(f"   Content length: {len(article_data['content_text'])} chars")
            print(f"   Authors: {article_data['author']}")
            
            return article_data
            
        except Exception as e:
            print(f"❌ Error scraping article: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


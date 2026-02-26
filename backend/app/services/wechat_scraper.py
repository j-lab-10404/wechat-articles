"""WeChat article scraper service."""
from newspaper import Article
from typing import Dict, Optional
from datetime import datetime
import requests
from ..config import settings


class WeChatScraper:
    """Scrape WeChat articles using newspaper3k with optional ScraperAPI."""
    
    def __init__(self):
        self.scraperapi_key = settings.SCRAPERAPI_KEY
        self.use_scraperapi = bool(self.scraperapi_key)
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape article from WeChat URL.
        
        Uses ScraperAPI if configured, otherwise uses newspaper3k directly.
        
        Args:
            url: WeChat article URL
            
        Returns:
            Dict with article data or None if failed
        """
        try:
            print(f"Scraping URL: {url}")
            print(f"Using ScraperAPI: {self.use_scraperapi}")
            
            if self.use_scraperapi:
                return self._scrape_with_scraperapi(url)
            else:
                return self._scrape_with_newspaper(url)
            
        except Exception as e:
            print(f"❌ Error scraping article: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _scrape_with_scraperapi(self, url: str) -> Optional[Dict]:
        """Scrape using ScraperAPI proxy."""
        try:
            print("   Using ScraperAPI to fetch content...")
            
            # Call ScraperAPI
            response = requests.get(
                'http://api.scraperapi.com',
                params={
                    'api_key': self.scraperapi_key,
                    'url': url,
                    'render': 'true',  # Enable JavaScript rendering
                    'country_code': 'cn'  # Use China proxy
                },
                timeout=60
            )
            response.raise_for_status()
            
            print(f"   ✅ ScraperAPI response: {response.status_code}")
            
            # Parse with newspaper3k
            article = Article(url, language='zh')
            article.download(input_html=response.text)
            article.parse()
            
            # Try NLP
            try:
                article.nlp()
            except Exception as e:
                print(f"   NLP processing failed: {str(e)}")
            
            # Extract data
            article_data = {
                'url': url,
                'title': article.title or "未知标题",
                'author': ', '.join(article.authors) if article.authors else None,
                'account_name': None,
                'content': article.html or response.text,
                'content_text': article.text or "",
                'published_at': article.publish_date or datetime.now(),
                'cover_image': article.top_image or None,
            }
            
            print(f"   ✅ Extracted:")
            print(f"      Title: {article_data['title']}")
            print(f"      Content length: {len(article_data['content_text'])} chars")
            
            return article_data
            
        except Exception as e:
            print(f"   ❌ ScraperAPI error: {str(e)}")
            raise
    
    def _scrape_with_newspaper(self, url: str) -> Optional[Dict]:
        """Scrape using newspaper3k directly (may fail due to anti-scraping)."""
        try:
            print("   Using newspaper3k directly...")
            
            # Create Article object
            article = Article(url, language='zh')
            
            # Download and parse
            article.download()
            article.parse()
            
            # Try NLP
            try:
                article.nlp()
            except Exception as e:
                print(f"   NLP processing failed: {str(e)}")
            
            # Extract data
            article_data = {
                'url': url,
                'title': article.title or "未知标题",
                'author': ', '.join(article.authors) if article.authors else None,
                'account_name': None,
                'content': article.html or "",
                'content_text': article.text or "",
                'published_at': article.publish_date or datetime.now(),
                'cover_image': article.top_image or None,
            }
            
            print(f"   ✅ Extracted:")
            print(f"      Title: {article_data['title']}")
            print(f"      Content length: {len(article_data['content_text'])} chars")
            
            return article_data
            
        except Exception as e:
            print(f"   ❌ Newspaper3k error: {str(e)}")
            raise



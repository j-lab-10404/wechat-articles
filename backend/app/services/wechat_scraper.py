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
            print(f"🔍 Scraping URL: {url}")
            print(f"🔑 ScraperAPI Key configured: {bool(self.scraperapi_key)}")
            print(f"🚀 Using ScraperAPI: {self.use_scraperapi}")
            
            if self.use_scraperapi:
                return self._scrape_with_scraperapi(url)
            else:
                return self._scrape_with_newspaper(url)
            
        except Exception as e:
            print(f"❌ Error scraping article: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise  # Re-raise to see error in API response
    
    def _scrape_with_scraperapi(self, url: str) -> Optional[Dict]:
        """Scrape using ScraperAPI proxy."""
        try:
            print("   📡 Using ScraperAPI to fetch content...")
            print(f"   🔑 API Key: {self.scraperapi_key[:10]}..." if self.scraperapi_key else "   ❌ No API Key")
            
            # Call ScraperAPI
            api_url = 'http://api.scraperapi.com'
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'true',  # Enable JavaScript rendering
                'country_code': 'cn'  # Use China proxy
            }
            
            print(f"   🌐 Calling ScraperAPI: {api_url}")
            print(f"   ⚙️  Parameters: render=true, country_code=cn")
            
            response = requests.get(
                api_url,
                params=params,
                timeout=60
            )
            
            print(f"   📊 ScraperAPI response status: {response.status_code}")
            print(f"   📏 Response length: {len(response.text)} bytes")
            
            response.raise_for_status()
            
            # Parse with newspaper3k
            print("   📰 Parsing with newspaper3k...")
            article = Article(url, language='zh')
            article.download(input_html=response.text)
            article.parse()
            
            print(f"   ✅ Parsed title: {article.title[:50]}..." if article.title else "   ⚠️  No title found")
            
            # Try NLP
            try:
                article.nlp()
                print("   🧠 NLP processing completed")
            except Exception as e:
                print(f"   ⚠️  NLP processing failed: {str(e)}")
            
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
            
            print(f"   ✅ Extraction complete:")
            print(f"      📝 Title: {article_data['title']}")
            print(f"      📊 Content length: {len(article_data['content_text'])} chars")
            print(f"      🖼️  Cover image: {bool(article_data['cover_image'])}")
            
            return article_data
            
        except requests.exceptions.HTTPError as e:
            print(f"   ❌ ScraperAPI HTTP error: {e}")
            print(f"   📄 Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
        except Exception as e:
            print(f"   ❌ ScraperAPI error: {str(e)}")
            print(f"   ❌ Error type: {type(e).__name__}")
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



"""WeChat article scraper service."""
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from datetime import datetime


class WeChatScraper:
    """Scrape WeChat articles."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def scrape_article(self, url: str) -> Optional[Dict]:
        """
        Scrape article from WeChat URL.
        
        Args:
            url: WeChat article URL
            
        Returns:
            Dict with article data or None if failed
        """
        try:
            # Validate URL
            if not self._is_valid_wechat_url(url):
                raise ValueError("Invalid WeChat article URL")
            
            # Fetch page
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            article_data = {
                'url': url,
                'title': self._extract_title(soup),
                'author': self._extract_author(soup),
                'account_name': self._extract_account_name(soup),
                'content': self._extract_content(soup),
                'content_text': self._extract_text_content(soup),
                'published_at': self._extract_publish_time(soup),
                'cover_image': self._extract_cover_image(soup),
            }
            
            return article_data
            
        except Exception as e:
            print(f"Error scraping article: {str(e)}")
            return None
    
    def _is_valid_wechat_url(self, url: str) -> bool:
        """Check if URL is a valid WeChat article URL."""
        pattern = r'https?://mp\.weixin\.qq\.com/s/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract article title."""
        # Try meta tag first
        meta_title = soup.find('meta', property='og:title')
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()
        
        # Try h1 tag
        h1 = soup.find('h1', class_='rich_media_title')
        if h1:
            return h1.get_text().strip()
        
        # Try title tag
        title = soup.find('title')
        if title:
            return title.get_text().strip()
        
        return "未知标题"
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author."""
        author_tag = soup.find('a', class_='rich_media_meta_link')
        if author_tag:
            return author_tag.get_text().strip()
        
        # Try meta tag
        meta_author = soup.find('meta', property='og:article:author')
        if meta_author and meta_author.get('content'):
            return meta_author['content'].strip()
        
        return None
    
    def _extract_account_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract WeChat account name."""
        account_tag = soup.find('strong', class_='profile_nickname')
        if account_tag:
            return account_tag.get_text().strip()
        
        account_tag = soup.find('a', id='js_name')
        if account_tag:
            return account_tag.get_text().strip()
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract article HTML content."""
        content_div = soup.find('div', class_='rich_media_content')
        if content_div:
            return str(content_div)
        
        content_div = soup.find('div', id='js_content')
        if content_div:
            return str(content_div)
        
        return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract article text content (no HTML)."""
        content_div = soup.find('div', class_='rich_media_content')
        if not content_div:
            content_div = soup.find('div', id='js_content')
        
        if content_div:
            # Remove script and style tags
            for tag in content_div(['script', 'style']):
                tag.decompose()
            
            # Get text
            text = content_div.get_text(separator='\n', strip=True)
            return text
        
        return ""
    
    def _extract_publish_time(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publish time."""
        # Try meta tag
        meta_time = soup.find('meta', property='og:article:published_time')
        if meta_time and meta_time.get('content'):
            try:
                return datetime.fromisoformat(meta_time['content'].replace('Z', '+00:00'))
            except:
                pass
        
        # Try em tag
        time_tag = soup.find('em', id='publish_time')
        if time_tag:
            time_str = time_tag.get_text().strip()
            try:
                return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
            except:
                pass
        
        # Return current time as fallback
        return datetime.now()
    
    def _extract_cover_image(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract cover image URL."""
        # Try meta tag
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            return meta_image['content']
        
        # Try first image in content
        content_div = soup.find('div', class_='rich_media_content')
        if not content_div:
            content_div = soup.find('div', id='js_content')
        
        if content_div:
            img = content_div.find('img')
            if img and img.get('data-src'):
                return img['data-src']
        
        return None

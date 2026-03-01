"""RSS service for fetching articles from WeWe-RSS."""
import httpx
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode
from ..config import settings


class RSSService:
    """Service for interacting with WeWe-RSS."""

    def __init__(self):
        self.base_url = settings.WEWE_RSS_URL.rstrip("/")
        self.auth_code = settings.WEWE_RSS_AUTH_CODE

    def _headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.auth_code:
            h["Authorization"] = f"Bearer {self.auth_code}"
        return h

    @staticmethod
    def _html_to_text(html: str) -> str:
        """Extract plain text from WeChat article HTML."""
        if not html:
            return ""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            div = soup.find(id="js_content")
            if not div:
                div = soup.find(class_="rich_media_content")
            text = div.get_text("\n", strip=True) if div else soup.get_text("\n", strip=True)
            return re.sub(r'\n{3,}', '\n\n', text).strip()
        except Exception:
            return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()

    @staticmethod
    def _get_biz(url: str) -> str:
        """Extract __biz param from WeChat URL."""
        try:
            return parse_qs(urlparse(url).query).get("__biz", [""])[0]
        except Exception:
            return ""

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize WeChat URL for matching."""
        if not url:
            return ""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            keep = {}
            for k in ("__biz", "mid", "idx", "sn"):
                if k in params:
                    keep[k] = params[k][0]
            if keep:
                return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(keep)}"
        except Exception:
            pass
        return url.split("#")[0]

    async def get_feeds(self) -> List[Dict]:
        """Get subscribed feeds from WeWe-RSS."""
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}/feeds")
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else data.get("data", [])

    async def add_feed(self, mp_url: str) -> Dict:
        """Subscribe to a feed via article URL."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/feeds",
                headers=self._headers(),
                json={"url": mp_url},
            )
            resp.raise_for_status()
            return resp.json()

    async def _find_feed_for_url(self, article_url: str) -> Optional[str]:
        """Find which feed contains the article by matching __biz."""
        target_biz = self._get_biz(article_url)
        if not target_biz:
            return None
        feeds = await self.get_feeds()
        for feed in feeds:
            mp_url = feed.get("mpUrl", "") or ""
            feed_biz = self._get_biz(mp_url)
            if feed_biz and feed_biz == target_biz:
                return feed.get("id")
        return None

    async def get_article_content(self, article_url: str) -> Optional[Dict]:
        """
        Fetch article content from WeWe-RSS.
        
        Strategy: find the specific feed first, then search only that feed.
        This avoids downloading all feeds (each ~3MB per article).
        """
        normalized = self._normalize_url(article_url)
        
        try:
            # Step 1: find which feed this article belongs to
            feed_id = await self._find_feed_for_url(article_url)
            
            if feed_id:
                print(f"[RSS] Found feed {feed_id} for article")
                result = await self._search_feed(feed_id, article_url, normalized)
                if result:
                    return result
            
            # Step 2: if not found by biz, search all feeds one by one
            print("[RSS] Biz match failed, searching all feeds...")
            feeds = await self.get_feeds()
            for feed in feeds:
                fid = feed.get("id", "")
                if fid and fid != feed_id:  # skip already-searched feed
                    result = await self._search_feed(fid, article_url, normalized)
                    if result:
                        return result
                        
        except Exception as e:
            print(f"[RSS] Error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"[RSS] Not found: {article_url[:80]}")
        return None

    async def _search_feed(self, feed_id: str, target_url: str, target_norm: str) -> Optional[Dict]:
        """Search a single feed for the target article."""
        try:
            url = f"{self.base_url}/feeds/{feed_id}.json?limit=50"
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.get(url)
                if resp.status_code != 200:
                    return None
                data = resp.json()
            
            for item in data.get("items", []):
                item_url = item.get("url", "")
                if item_url == target_url or self._normalize_url(item_url) == target_norm:
                    html = item.get("content_html", "")
                    text = item.get("content_text", "")
                    if not text and html:
                        text = self._html_to_text(html)
                    
                    author = item.get("author", "")
                    if isinstance(author, dict):
                        author = author.get("name", "")
                    
                    print(f"[RSS] Found: {item.get('title','?')}, {len(text)} chars")
                    return {
                        "title": item.get("title", ""),
                        "url": item_url,
                        "content_html": html,
                        "content_text": text,
                        "published_at": self._parse_date(item.get("date_published")),
                        "author": str(author or ""),
                    }
        except Exception as e:
            print(f"[RSS] Feed {feed_id} error: {e}")
        return None

    async def check_feed_exists(self, mp_url: str) -> Optional[Dict]:
        """Check if a feed is already subscribed."""
        try:
            feeds = await self.get_feeds()
            for feed in feeds:
                if isinstance(feed, dict):
                    feed_url = feed.get("mpUrl", "") or feed.get("url", "")
                    if feed_url and self._get_biz(feed_url) == self._get_biz(mp_url):
                        return feed
        except Exception as e:
            print(f"Error checking feed: {e}")
        return None

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

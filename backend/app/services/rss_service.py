"""RSS service for fetching articles from WeWe-RSS."""
import httpx
import re
from typing import List, Dict, Optional
from datetime import datetime
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
        """Extract plain text from HTML."""
        if not html:
            return ""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            content_div = soup.find(id="js_content")
            if not content_div:
                content_div = soup.find(class_="rich_media_content")
            if content_div:
                text = content_div.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()
        except Exception:
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize WeChat article URL."""
        if not url:
            return ""
        from urllib.parse import urlparse, parse_qs, urlencode
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
        """Get all subscribed feeds."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/feeds")
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return []

    async def add_feed(self, mp_url: str) -> Dict:
        """Add a feed via article URL."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/feeds",
                headers=self._headers(),
                json={"url": mp_url},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_article_content(self, article_url: str) -> Optional[Dict]:
        """
        Fetch article content from WeWe-RSS by searching each feed.
        """
        normalized_target = self._normalize_url(article_url)
        try:
            feeds = await self.get_feeds()
            print(f"[RSS] {len(feeds)} feeds, looking for: {article_url[:80]}")

            for feed in feeds:
                feed_id = feed.get("id", "")
                feed_name = feed.get("name", "?")
                if not feed_id:
                    continue
                try:
                    feed_url = f"{self.base_url}/feeds/{feed_id}.json?limit=30"
                    print(f"[RSS] Checking feed: {feed_name}")
                    async with httpx.AsyncClient(timeout=180) as client:
                        resp = await client.get(feed_url)
                        if resp.status_code != 200:
                            continue
                        data = resp.json()
                    for item in data.get("items", []):
                        item_url = item.get("url", "")
                        item_norm = self._normalize_url(item_url)
                        if item_url == article_url or item_norm == normalized_target:
                            html = item.get("content_html", "")
                            text = item.get("content_text", "")
                            if not text and html:
                                text = self._html_to_text(html)
                            author_raw = item.get("author", "")
                            if isinstance(author_raw, dict):
                                author = author_raw.get("name", "")
                            else:
                                author = str(author_raw or "")
                            print(f"[RSS] Found: {item.get('title','?')}, {len(text)} chars")
                            return {
                                "title": item.get("title", ""),
                                "url": item_url,
                                "content_html": html,
                                "content_text": text,
                                "published_at": self._parse_date(item.get("date_published")),
                                "author": author,
                            }
                except Exception as e:
                    print(f"[RSS] Feed {feed_name} error: {e}")
                    continue
        except Exception as e:
            print(f"[RSS] Error: {e}")
            import traceback
            traceback.print_exc()
        print(f"[RSS] Not found: {article_url[:80]}")
        return None

    async def check_feed_exists(self, mp_url: str) -> Optional[Dict]:
        """Check if a feed is already subscribed."""
        try:
            feeds = await self.get_feeds()
            for feed in feeds:
                if isinstance(feed, dict):
                    feed_url = feed.get("mpUrl", "") or feed.get("url", "")
                    if feed_url and self._same_account(feed_url, mp_url):
                        return feed
        except Exception as e:
            print(f"Error checking feed: {e}")
        return None

    @staticmethod
    def _same_account(url1: str, url2: str) -> bool:
        from urllib.parse import urlparse, parse_qs
        try:
            q1 = parse_qs(urlparse(url1).query)
            q2 = parse_qs(urlparse(url2).query)
            biz1 = q1.get("__biz", [""])[0]
            biz2 = q2.get("__biz", [""])[0]
            if biz1 and biz2:
                return biz1 == biz2
        except Exception:
            pass
        return False

    @staticmethod
    def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

"""RSS service for fetching articles from WeWe-RSS."""
import httpx
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

    async def get_feeds(self) -> List[Dict]:
        """获取所有已订阅的公众号列表."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{self.base_url}/api/feeds", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def add_feed(self, mp_url: str) -> Dict:
        """通过公众号文章链接添加订阅."""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/api/feeds",
                headers=self._headers(),
                json={"url": mp_url},
            )
            resp.raise_for_status()
            return resp.json()

    async def get_feed_articles(self, feed_id: str, limit: int = 50) -> List[Dict]:
        """获取某个公众号的文章列表（JSON Feed 格式）."""
        url = f"{self.base_url}/feeds/{feed_id}.json?limit={limit}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        articles = []
        for item in data.get("items", []):
            articles.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content_html": item.get("content_html", ""),
                "content_text": item.get("content_text", ""),
                "published_at": self._parse_date(item.get("date_published")),
                "author": item.get("author", {}).get("name", ""),
            })
        return articles

    async def get_all_articles(self, limit: int = 50) -> List[Dict]:
        """获取所有订阅公众号的文章."""
        url = f"{self.base_url}/feeds/all.json?limit={limit}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        articles = []
        for item in data.get("items", []):
            articles.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content_html": item.get("content_html", ""),
                "content_text": item.get("content_text", ""),
                "published_at": self._parse_date(item.get("date_published")),
                "author": item.get("author", {}).get("name", ""),
            })
        return articles

    async def get_article_content(self, article_url: str) -> Optional[Dict]:
        """
        从 WeWe-RSS 的 feed 中查找指定 URL 的文章全文.
        遍历所有 feed 查找匹配的文章。
        """
        try:
            all_articles = await self.get_all_articles(limit=200)
            for article in all_articles:
                if article["url"] == article_url:
                    return article
        except Exception as e:
            print(f"Error fetching article content: {e}")
        return None

    async def check_feed_exists(self, mp_url: str) -> Optional[Dict]:
        """检查公众号是否已订阅."""
        try:
            feeds = await self.get_feeds()
            # WeWe-RSS 的 feed 列表中查找匹配
            for feed in feeds:
                if isinstance(feed, dict):
                    # 简单匹配：检查 biz 参数
                    feed_url = feed.get("mpUrl", "") or feed.get("url", "")
                    if feed_url and self._same_account(feed_url, mp_url):
                        return feed
        except Exception as e:
            print(f"Error checking feed: {e}")
        return None

    @staticmethod
    def _same_account(url1: str, url2: str) -> bool:
        """判断两个链接是否来自同一个公众号."""
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

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
        """从 HTML 中提取纯文本，优先提取微信文章正文区域."""
        if not html:
            return ""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # 移除 script / style 标签
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            # 优先取微信正文区域
            content_div = soup.find(id="js_content") or soup.find(class_="rich_media_content")
            if content_div:
                text = content_div.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # 清理多余空行
            text = re.sub(r'\n{3,}', '\n\n', text)
            return text.strip()
        except Exception:
            # fallback: 简单正则去标签
            text = re.sub(r'<[^>]+>', ' ', html)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    @staticmethod
    def _normalize_url(url: str) -> str:
        """标准化微信文章 URL，去掉追踪参数以便匹配."""
        if not url:
            return ""
        from urllib.parse import urlparse, parse_qs, urlencode
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            # 保留核心参数
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
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        return self._parse_feed_items(data)

    async def get_all_articles(self, limit: int = 50) -> List[Dict]:
        """获取所有订阅公众号的文章（不含全文，用于列表/匹配）."""
        url = f"{self.base_url}/feeds/all.json?limit={limit}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
        return self._parse_feed_items(data)

    async def get_article_content(self, article_url: str) -> Optional[Dict]:
        """
        从 WeWe-RSS 获取指定 URL 的文章全文.

        策略：
        1. 先用 all.json 获取文章列表（含 content_html）
        2. 通过 URL 匹配找到目标文章
        3. 从 content_html 提取纯文本
        """
        try:
            normalized_target = self._normalize_url(article_url)

            # 获取文章列表（WeWe-RSS fulltext 模式下 content_html 包含全文）
            all_articles = await self.get_all_articles(limit=200)

            for article in all_articles:
                article_normalized = self._normalize_url(article.get("url", ""))
                # 精确匹配或标准化匹配
                if article["url"] == article_url or article_normalized == normalized_target:
                    # 确保有纯文本内容
                    if not article.get("content_text") and article.get("content_html"):
                        article["content_text"] = self._html_to_text(article["content_html"])
                    return article

        except Exception as e:
            print(f"Error fetching article content: {e}")
            import traceback
            traceback.print_exc()
        return None

    async def check_feed_exists(self, mp_url: str) -> Optional[Dict]:
        """检查公众号是否已订阅."""
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

    def _parse_feed_items(self, data: dict) -> List[Dict]:
        """解析 JSON Feed 的 items."""
        articles = []
        for item in data.get("items", []):
            content_html = item.get("content_html", "")
            content_text = item.get("content_text", "")

            # 如果没有纯文本但有 HTML，提取文本
            if not content_text and content_html:
                content_text = self._html_to_text(content_html)

            articles.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content_html": content_html,
                "content_text": content_text,
                "published_at": self._parse_date(item.get("date_published")),
                "author": item.get("author", {}).get("name", "") if isinstance(item.get("author"), dict) else "",
            })
        return articles

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

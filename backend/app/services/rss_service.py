"""RSS service for fetching articles from WeWe-RSS + direct scraping."""
import httpx
import re
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode
from ..config import settings

MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/16.0 Mobile/15E148 Safari/604.1"
)


class RSSService:

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
            if div:
                return re.sub(r'\n{3,}', '\n\n', div.get_text("\n", strip=True)).strip()
            return re.sub(r'\n{3,}', '\n\n', soup.get_text("\n", strip=True)).strip()
        except Exception:
            return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html)).strip()

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        essential = {}
        for key in ["__biz", "mid", "idx", "sn"]:
            if key in params:
                essential[key] = params[key][0]
        if essential:
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(essential)}"
        return url.split("#")[0].rstrip("/")

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        if not date_str:
            return None
        for fmt in [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    # ── Direct scraping (primary method) ────────────────────────

    async def _scrape_direct(self, url: str) -> Optional[Dict]:
        """Scrape WeChat article directly with mobile UA."""
        try:
            async with httpx.AsyncClient(
                follow_redirects=True, timeout=20.0
            ) as client:
                resp = await client.get(url, headers={"User-Agent": MOBILE_UA})
                if resp.status_code != 200:
                    print(f"Direct scrape failed: HTTP {resp.status_code}")
                    return None

                html = resp.text
                if len(html) < 500 or "环境异常" in html:
                    print("Direct scrape: got verification page")
                    return None

                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, "html.parser")

                # Title
                title = ""
                title_el = soup.find(id="activity-name")
                if title_el:
                    title = title_el.get_text(strip=True)
                if not title:
                    og = soup.find("meta", property="og:title")
                    if og:
                        title = og.get("content", "")

                # Author
                author = ""
                author_el = soup.find(id="js_name")
                if author_el:
                    author = author_el.get_text(strip=True)

                # Published date
                pub_date = None
                pub_match = re.search(r'var ct\s*=\s*"(\d+)"', html)
                if pub_match:
                    try:
                        pub_date = datetime.fromtimestamp(int(pub_match.group(1)))
                    except Exception:
                        pass

                content_text = self._html_to_text(html)

                if not content_text or len(content_text) < 50:
                    print("Direct scrape: content too short")
                    return None

                return {
                    "title": title,
                    "author": author,
                    "content_html": html,
                    "content_text": content_text,
                    "published_at": pub_date,
                }
        except Exception as e:
            print(f"Direct scrape error: {e}")
            return None

    # ── WeWe-RSS fallback ───────────────────────────────────────

    async def get_feeds(self) -> List[Dict]:
        """Get all feeds from WeWe-RSS."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{self.base_url}/feeds", headers=self._headers()
            )
            resp.raise_for_status()
            data = resp.json()
            # WeWe-RSS returns array directly
            return data if isinstance(data, list) else data.get("data", [])

    async def _search_feed(self, feed_id: str, target_url: str, limit: int = 3) -> Optional[Dict]:
        """Search a single feed for a matching article URL."""
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.get(
                    f"{self.base_url}/feeds/{feed_id}.json?limit={limit}",
                    headers=self._headers(),
                )
                if resp.status_code != 200:
                    return None
                data = resp.json()
                items = data.get("items", [])
                norm_target = self._normalize_url(target_url)
                for item in items:
                    item_url = item.get("url", "")
                    if not item_url:
                        continue
                    if (norm_target in self._normalize_url(item_url)
                            or self._normalize_url(item_url) in norm_target
                            or item_url.rstrip("/") == target_url.rstrip("/")):
                        content_html = item.get("content_html", "")
                        content_text = self._html_to_text(content_html)
                        return {
                            "title": item.get("title", ""),
                            "author": item.get("authors", [{}])[0].get("name", "") if item.get("authors") else "",
                            "content_html": content_html,
                            "content_text": content_text,
                            "published_at": self._parse_date(item.get("date_published")),
                        }
        except Exception as e:
            print(f"Feed {feed_id} search error: {e}")
        return None

    async def _search_wewe_rss(self, url: str) -> Optional[Dict]:
        """Search all WeWe-RSS feeds for the article (fallback)."""
        try:
            feeds = await self.get_feeds()
            for feed in feeds:
                feed_id = feed.get("id")
                if not feed_id:
                    continue
                result = await self._search_feed(feed_id, url, limit=5)
                if result and result.get("content_text"):
                    return result
        except Exception as e:
            print(f"WeWe-RSS search error: {e}")
        return None

    # ── Public API ──────────────────────────────────────────────

    async def get_article_content(self, url: str) -> Optional[Dict]:
        """
        Get article content. Strategy:
        1. Direct scrape with mobile UA (fast, ~3-6s)
        2. Fallback to WeWe-RSS feed search (slower, may timeout on Render)
        """
        # Primary: direct scraping
        result = await self._scrape_direct(url)
        if result and result.get("content_text"):
            print(f"Got content via direct scrape: {len(result['content_text'])} chars")
            return result

        # Fallback: WeWe-RSS
        print("Direct scrape failed, trying WeWe-RSS fallback...")
        result = await self._search_wewe_rss(url)
        if result and result.get("content_text"):
            print(f"Got content via WeWe-RSS: {len(result['content_text'])} chars")
            return result

        print("All content fetch methods failed")
        return None

    async def add_feed(self, url: str) -> Dict:
        """Add a new feed to WeWe-RSS."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.base_url}/feeds",
                headers=self._headers(),
                json={"url": url},
            )
            resp.raise_for_status()
            return resp.json()

    async def check_feed_exists(self, mp_name: str) -> Optional[Dict]:
        """Check if a feed for a given MP account already exists."""
        feeds = await self.get_feeds()
        for feed in feeds:
            if feed.get("mpName") == mp_name or feed.get("title") == mp_name:
                return feed
        return None

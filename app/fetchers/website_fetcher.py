"""
Website Fetcher

دریافت خبر از وب‌سایت‌هایی که RSS ندارند.
"""

from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.logger import logger


class WebsiteFetcher(BaseFetcher):
    """
    دریافت خبر از وب‌سایت.
    """

    def __init__(self, source):
        super().__init__(source)

        self.timeout = aiohttp.ClientTimeout(
            total=20
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            )
        }

    async def fetch(self) -> List[RawNews]:
        """
        دریافت خبرها از وب‌سایت.
        """

        logger.info(
            f"Fetching website: {self.source.name}"
        )

        news_list: List[RawNews] = []

        if not self.source.supports_scraping:
            logger.warning(
                f"{self.source.name} does not support scraping."
            )
            return news_list

        website_url = (
            getattr(
                self.source,
                "website_url",
                None
            )
            or getattr(
                self.source,
                "url",
                ""
            )
        )

        if not website_url:
            logger.warning(
                f"No website URL for {self.source.name}"
            )
            return news_list

        try:

            html = await self._download_page(
                website_url
            )

            if not html:
                return news_list

            soup = BeautifulSoup(
                html,
                "lxml"
            )

            # --------------------------------------------------
            # Parser اختصاصی
            # --------------------------------------------------

            custom_news = await self._custom_parser(
                soup,
                website_url
            )

            if custom_news:
                return custom_news

            # --------------------------------------------------
            # Parser عمومی
            # --------------------------------------------------

            news_list = self._parse_generic_page(
                soup,
                website_url
            )

            logger.info(
                f"{self.source.name}: "
                f"{len(news_list)} news found"
            )

        except Exception as e:

            logger.exception(
                f"Website fetch failed for "
                f"{self.source.name}: {e}"
            )

        return news_list

    async def _download_page(
        self,
        url: str
    ) -> Optional[str]:
        """
        دریافت HTML صفحه.
        """

        try:

            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers
            ) as session:

                async with session.get(
                    url,
                    allow_redirects=True
                ) as response:

                    if response.status != 200:

                        logger.warning(
                            f"{self.source.name}: "
                            f"HTTP {response.status} "
                            f"for {url}"
                        )

                        return None

                    content_type = response.headers.get(
                        "Content-Type",
                        ""
                    ).lower()

                    if (
                        "text/html" not in content_type
                        and "application/xhtml" not in content_type
                    ):
                        logger.warning(
                            f"{self.source.name}: "
                            f"Not an HTML page"
                        )

                        return None

                    return await response.text(
                        errors="ignore"
                    )

        except Exception as e:

            logger.warning(
                f"Cannot download {url}: {e}"
            )

            return None

    async def _custom_parser(
        self,
        soup: BeautifulSoup,
        base_url: str
    ) -> List[RawNews]:
        """
        محل Parser اختصاصی منابع.

        در آینده برای منابعی مثل:
        Fabrizio Romano
        Sky Sports
        The Athletic
        Vahid Online
        Hengaw
        Tasnim
        Fars
        و ...
        Parser اختصاصی اضافه می‌کنیم.

        فعلاً Parser اختصاصی نداریم.
        """

        return []

    def _parse_generic_page(
        self,
        soup: BeautifulSoup,
        base_url: str
    ) -> List[RawNews]:
        """
        Parser عمومی برای سایت‌هایی که
        ساختار استاندارد HTML دارند.
        """

        news_list: List[RawNews] = []

        seen_urls = set()

        # ------------------------------------------------------
        # پیدا کردن لینک‌های احتمالی خبر
        # ------------------------------------------------------

        candidates = soup.find_all(
            "a",
            href=True
        )

        for link in candidates:

            try:

                href = link.get("href", "").strip()

                if not href:
                    continue

                article_url = urljoin(
                    base_url,
                    href
                )

                if not self._is_valid_article_url(
                    article_url,
                    base_url
                ):
                    continue

                if article_url in seen_urls:
                    continue

                title = link.get_text(
                    " ",
                    strip=True
                )

                if not title:
                    continue

                # عنوان‌های خیلی کوتاه معمولاً منوی سایت هستند.
                if len(title) < 20:
                    continue

                # عنوان‌های بسیار طولانی معمولاً متن صفحه هستند.
                if len(title) > 300:
                    continue

                seen_urls.add(article_url)

                image_url = self._extract_image_from_link(
                    link,
                    base_url
                )

                news = RawNews(
                    source_id=self.source.id,

                    source=self.source.name,

                    title=title,

                    content="",

                    summary="",

                    url=article_url,

                    image_url=image_url or "",

                    author="",

                    published_at=None,

                    language=self.source.language,

                    category=(
                        self.source.categories[0]
                        if getattr(
                            self.source,
                            "categories",
                            None
                        )
                        else ""
                    ),

                    raw_data={
                        "fetcher": "website",
                        "source_url": base_url,
                    },

                )

                news_list.append(news)

                # جلوگیری از تولید تعداد بسیار زیاد
                # لینک از صفحه اصلی.
                if len(news_list) >= 30:
                    break

            except Exception as e:

                logger.warning(
                    f"Error parsing website item "
                    f"from {self.source.name}: {e}"
                )

        return news_list

    @staticmethod
    def _is_valid_article_url(
        article_url: str,
        base_url: str
    ) -> bool:
        """
        بررسی اولیه لینک خبر.
        """

        try:

            article = urlparse(
                article_url
            )

            base = urlparse(
                base_url
            )

            if not article.scheme:
                return False

            if article.scheme not in (
                "http",
                "https"
            ):
                return False

            # فقط لینک‌های همان دامنه
            if article.netloc != base.netloc:
                return False

            # حذف لینک‌های غیرخبری رایج
            blocked_parts = (
                "/tag/",
                "/tags/",
                "/category/",
                "/categories/",
                "/author/",
                "/search",
                "/login",
                "/register",
                "/privacy",
                "/terms",
                "#",
                "javascript:"
            )

            lowered = article.path.lower()

            for part in blocked_parts:

                if part in lowered:
                    return False

            return True

        except Exception:
            return False

    @staticmethod
    def _extract_image_from_link(
        link,
        base_url: str
    ) -> Optional[str]:
        """
        تلاش برای پیدا کردن تصویر خبر
        از داخل لینک یا والد آن.
        """

        # تصویر مستقیم داخل <a>
        image = link.find("img")

        if image:

            for attribute in (
                "src",
                "data-src",
                "data-lazy-src",
                "data-original"
            ):

                value = image.get(
                    attribute
                )

                if value:
                    return urljoin(
                        base_url,
                        value
                    )

        # تصویر در والد
        parent = link.parent

        if parent:

            image = parent.find("img")

            if image:

                for attribute in (
                    "src",
                    "data-src",
                    "data-lazy-src",
                    "data-original"
                ):

                    value = image.get(
                        attribute
                    )

                    if value:
                        return urljoin(
                            base_url,
                            value
                        )

        return None

"""
Website Fetcher
دریافت خبر از وب‌سایت‌هایی که RSS ندارند.
"""

import asyncio
import json
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional
from urllib.parse import (
    urljoin,
    urlparse,
    urldefrag,
    parse_qsl,
    urlencode,
)

import aiohttp
from bs4 import BeautifulSoup

from app.fetchers.base_fetcher import BaseFetcher
from app.models.raw_news import RawNews
from app.utils.logger import logger


class WebsiteFetcher(BaseFetcher):
    """دریافت خبر از وب‌سایت و استخراج اطلاعات مقاله."""

    MAX_NEWS = 30
    MAX_ARTICLES_TO_ENRICH = 10
    MAX_TEXT_LENGTH = 12000

    def __init__(self, source):
        super().__init__(source)

        self.timeout = aiohttp.ClientTimeout(
            total=15,
            connect=5,
            sock_read=10,
        )

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9,fa;q=0.8",
        }

    async def fetch(self) -> List[RawNews]:
        """دریافت خبرها از صفحه اصلی یا صفحه اخبار منبع."""

        logger.info("Fetching website: %s", self.source.name)

        if not getattr(self.source, "supports_scraping", False):
            logger.warning(
                "%s does not support scraping.",
                self.source.name,
            )
            return []

        website_url = (
            getattr(self.source, "website_url", None)
            or getattr(self.source, "url", "")
        )

        if not website_url:
            logger.warning(
                "No website URL for %s",
                self.source.name,
            )
            return []

        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers=self.headers,
            ) as session:
                html = await self._download_page(
                    session,
                    website_url,
                )

                if not html:
                    return []

                soup = BeautifulSoup(html, "lxml")

                news_list = await self._custom_parser(
                    soup,
                    website_url,
                    session,
                )

                if not news_list:
                    news_list = self._parse_generic_page(
                        soup,
                        website_url,
                    )

                # تکمیل متن خبرها با مراجعه به صفحات مقاله.
                # برای جلوگیری از درخواست‌های بیش از حد، تعداد محدود است.
                to_enrich = [
                    news
                    for news in news_list
                    if news.url
                    and (not news.content or len(news.content) < 200)
                ][:self.MAX_ARTICLES_TO_ENRICH]

                semaphore = asyncio.Semaphore(5)

                async def enrich_one(news):
                    async with semaphore:
                        try:
                            await self._enrich_article(
                                session,
                                news,
                            )
                        except Exception as error:
                            logger.debug(
                                "Article enrichment failed for %s: %s",
                                news.url,
                                error,
                            )

                if to_enrich:
                    await asyncio.gather(
                        *(enrich_one(news) for news in to_enrich)
                    )

                logger.info(
                    "%s: %d news found",
                    self.source.name,
                    len(news_list),
                )

                return news_list[:self.MAX_NEWS]

        except Exception as error:
            logger.exception(
                "Website fetch failed for %s: %s",
                self.source.name,
                error,
            )
            return []

    async def _download_page(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> Optional[str]:
        """دانلود HTML یک صفحه."""

        try:
            async with session.get(
                url,
                allow_redirects=True,
            ) as response:
                if response.status != 200:
                    logger.warning(
                        "%s: HTTP %s for %s",
                        self.source.name,
                        response.status,
                        url,
                    )
                    return None

                content_type = response.headers.get(
                    "Content-Type",
                    "",
                ).lower()

                if (
                    "text/html" not in content_type
                    and "application/xhtml" not in content_type
                ):
                    logger.warning(
                        "%s: response is not HTML: %s",
                        self.source.name,
                        url,
                    )
                    return None

                return await response.text(errors="ignore")

        except (aiohttp.ClientError, asyncio.TimeoutError) as error:
            logger.warning(
                "Cannot download %s: %s",
                url,
                error,
            )
            return None

    async def _custom_parser(
        self,
        soup: BeautifulSoup,
        base_url: str,
        session: aiohttp.ClientSession,
    ) -> List[RawNews]:
        """
        محل افزودن Parser اختصاصی سایت‌ها.

        در حال حاضر Parser اختصاصی فعال نیست.
        منابع از Parser عمومی استفاده می‌کنند.
        """
        return []

    def _parse_generic_page(
        self,
        soup: BeautifulSoup,
        base_url: str,
    ) -> List[RawNews]:
        """استخراج خبرهای احتمالی از لینک‌های صفحه."""

        news_list: List[RawNews] = []
        seen_urls = set()

        for link in soup.find_all("a", href=True):
            if len(news_list) >= self.MAX_NEWS:
                break

            try:
                href = str(link.get("href", "")).strip()
                if not href:
                    continue

                article_url = self._normalize_url(
                    urljoin(base_url, href)
                )

                if not self._is_valid_article_url(
                    article_url,
                    base_url,
                ):
                    continue

                if article_url in seen_urls:
                    continue

                title = self._clean_text(
                    link.get("aria-label")
                    or link.get_text(" ", strip=True)
                )

                # اگر خود لینک عنوان نداشت، از تصویر داخل لینک کمک بگیر.
                if not title:
                    image = link.find("img")
                    if image:
                        title = self._clean_text(
                            image.get("alt", "")
                        )

                if not self._is_plausible_title(title):
                    continue

                seen_urls.add(article_url)

                card = self._find_article_container(link)
                image_url = self._extract_image(
                    link,
                    card,
                    soup,
                    base_url,
                )

                description = ""
                if card:
                    description = self._extract_card_description(
                        card,
                        title,
                    )

                category_hint = list(
                    getattr(self.source, "categories", None) or []
                )

                news = RawNews(
                    source_id=self.source.id,
                    source=self.source.name,
                    title=title,
                    content=description,
                    summary=description,
                    url=article_url,
                    image_url=image_url or "",
                    author="",
                    published_at=None,
                    language=getattr(
                        self.source,
                        "language",
                        "",
                    ),
                    country=getattr(
                        self.source,
                        "country",
                        "",
                    ),
                    category=(
                        category_hint[0]
                        if category_hint
                        else ""
                    ),
                    source_category_hint=category_hint,
                    raw_data={
                        "fetcher": "website",
                        "source_url": base_url,
                    },
                )

                news_list.append(news)

            except Exception as error:
                logger.debug(
                    "Error parsing item from %s: %s",
                    self.source.name,
                    error,
                )

        return news_list

    async def _enrich_article(
        self,
        session: aiohttp.ClientSession,
        news: RawNews,
    ) -> None:
        """استخراج متن و اطلاعات تکمیلی از صفحه خود مقاله."""

        html = await self._download_page(session, news.url)
        if not html:
            return

        soup = BeautifulSoup(html, "lxml")

        # متادیتای مقاله
        meta_title = self._get_meta(
            soup,
            ("og:title", "twitter:title"),
        )
        if meta_title and (
            not news.title or len(meta_title) > len(news.title)
        ):
            news.title = meta_title

        meta_description = self._get_meta(
            soup,
            (
                "og:description",
                "twitter:description",
                "description",
            ),
        )

        meta_image = self._get_meta(
            soup,
            ("og:image", "twitter:image"),
        )
        if meta_image and not news.image_url:
            news.image_url = urljoin(news.url, meta_image)

        author = self._get_meta(
            soup,
            ("author", "article:author"),
        )
        if author and not news.author:
            news.author = author

        published = self._get_meta(
            soup,
            (
                "article:published_time",
                "datePublished",
                "pubdate",
            ),
        )
        if published:
            parsed_date = self._parse_datetime(published)
            if parsed_date:
                news.published_at = parsed_date

        # حذف بخش‌هایی که معمولاً متن خبر نیستند.
        for element in soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header",
                "aside",
                "form",
                "button",
                "svg",
            ]
        ):
            element.decompose()

        article = (
            soup.find("article")
            or soup.find("main")
            or soup.find(
                attrs={
                    "itemprop": "articleBody",
                }
            )
        )

        if article:
            text = self._clean_text(
                article.get_text(" ", strip=True)
            )
        else:
            text = self._extract_paragraph_text(soup)

        if text and len(text) > len(news.content or ""):
            news.content = text[:self.MAX_TEXT_LENGTH]

        if not news.summary:
            news.summary = meta_description or (
                news.content[:500]
                if news.content
                else ""
            )

        # نگهداری متادیتای استخراج‌شده برای بررسی‌های بعدی
        news.raw_data.update({
            "article_enriched": True,
            "article_meta_description": meta_description or "",
        })

    @staticmethod
    def _extract_paragraph_text(
        soup: BeautifulSoup,
    ) -> str:
        """جمع‌آوری پاراگراف‌های مناسب وقتی article یا main وجود ندارد."""

        paragraphs = []

        for paragraph in soup.find_all("p"):
            text = WebsiteFetcher._clean_text(
                paragraph.get_text(" ", strip=True)
            )

            if len(text) >= 40:
                paragraphs.append(text)

        # حذف پاراگراف‌های تکراری
        unique = list(dict.fromkeys(paragraphs))
        return " ".join(unique)[:WebsiteFetcher.MAX_TEXT_LENGTH]

    @staticmethod
    def _find_article_container(link):
        """یافتن کارت یا ظرف احتمالی خبر."""

        current = link

        for _ in range(4):
            if not current or not getattr(current, "parent", None):
                break

            current = current.parent

            name = getattr(current, "name", "")
            classes = " ".join(
                current.get("class", [])
            ).lower() if hasattr(current, "get") else ""

            if (
                name in ("article", "li")
                or any(
                    marker in classes
                    for marker in (
                        "article",
                        "story",
                        "news-item",
                        "post",
                        "card",
                    )
                )
            ):
                return current

        return link.parent

    @staticmethod
    def _extract_card_description(card, title: str) -> str:
        """پیداکردن خلاصه از کارت خبر."""

        for selector in (
            "p",
            '[class*="summary"]',
            '[class*="excerpt"]',
            '[class*="description"]',
        ):
            element = card.select_one(selector)

            if not element:
                continue

            text = WebsiteFetcher._clean_text(
                element.get_text(" ", strip=True)
            )

            if text and text != title and len(text) >= 30:
                return text[:1000]

        return ""

    @staticmethod
    def _extract_image(
        link,
        card,
        soup: BeautifulSoup,
        base_url: str,
    ) -> Optional[str]:
        """استخراج تصویر از لینک، کارت خبر یا متادیتای صفحه."""

        containers = [link]
        if card and card is not link:
            containers.append(card)

        for container in containers:
            image = container.find("img")

            if image:
                for attribute in (
                    "src",
                    "data-src",
                    "data-lazy-src",
                    "data-original",
                    "data-srcset",
                ):
                    value = image.get(attribute)

                    if value:
                        # srcset ممکن است چند اندازه تصویر داشته باشد.
                        value = str(value).split(",")[0].strip().split(" ")[0]

                        if value.startswith("data:"):
                            continue

                        return urljoin(base_url, value)

        # fallback به تصویر معرفی‌شده در صفحه
        for attribute in (
            ("property", "og:image"),
            ("name", "twitter:image"),
        ):
            meta = soup.find("meta", attrs={attribute[0]: attribute[1]})
            if meta and meta.get("content"):
                value = meta["content"].strip()
                if value and not value.startswith("data:"):
                    return urljoin(base_url, value)

        return None

    @staticmethod
    def _get_meta(
        soup: BeautifulSoup,
        keys,
    ) -> Optional[str]:
        """جست‌وجوی متادیتا با چند نام رایج."""

        for key in keys:
            meta = soup.find(
                "meta",
                attrs={"property": key},
            ) or soup.find(
                "meta",
                attrs={"name": key},
            )

            if meta and meta.get("content"):
                value = WebsiteFetcher._clean_text(
                    meta.get("content", "")
                )
                if value:
                    return value

            # پشتیبانی ابتدایی از JSON-LD
            if key in ("datePublished", "author"):
                for script in soup.find_all(
                    "script",
                    attrs={"type": "application/ld+json"},
                ):
                    try:
                        data = json.loads(script.string or script.get_text())
                        objects = data if isinstance(data, list) else [data]

                        for obj in objects:
                            if not isinstance(obj, dict):
                                continue

                            candidates = [obj]
                            if isinstance(obj.get("@graph"), list):
                                candidates.extend(obj["@graph"])

                            for candidate in candidates:
                                if not isinstance(candidate, dict):
                                    continue

                                value = candidate.get(key)
                                if isinstance(value, dict):
                                    value = (
                                        value.get("name")
                                        or value.get("datePublished")
                                    )

                                if isinstance(value, str) and value.strip():
                                    return value.strip()
                    except (ValueError, TypeError):
                        continue

        return None

    @staticmethod
    def _parse_datetime(value: str) -> Optional[datetime]:
        """تبدیل تاریخ‌های رایج به datetime."""

        if not value:
            return None

        value = value.strip()

        try:
            parsed = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
            if parsed.tzinfo:
                return parsed.astimezone(timezone.utc).replace(
                    tzinfo=None
                )
            return parsed
        except ValueError:
            pass

        try:
            parsed = parsedate_to_datetime(value)
            if parsed.tzinfo:
                return parsed.astimezone(timezone.utc).replace(
                    tzinfo=None
                )
            return parsed
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _clean_text(value: str) -> str:
        """یکنواخت‌سازی فاصله‌ها و حذف نویز متنی."""

        if not value:
            return ""

        value = value.replace("\xa0", " ")
        value = re.sub(r"\s+", " ", value)
        return value.strip()

    @staticmethod
    def _normalize_url(url: str) -> str:
        """حذف fragment و پارامترهای رهگیری رایج."""

        url, _fragment = urldefrag(url)
        parsed = urlparse(url)

        blocked_tracking = {
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
        }

        query = [
            (key, value)
            for key, value in parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
            if not key.lower().startswith("utm_")
            and key.lower() not in blocked_tracking
        ]

        return parsed._replace(
            query=urlencode(query),
            fragment="",
        ).geturl().rstrip("/")

    @staticmethod
    def _is_valid_article_url(
        article_url: str,
        base_url: str,
    ) -> bool:
        """بررسی اولیه اعتبار لینک مقاله."""

        try:
            article = urlparse(article_url)
            base = urlparse(base_url)

            if article.scheme not in ("http", "https"):
                return False

            if article.netloc.lower() != base.netloc.lower():
                return False

            path = article.path.lower()

            if not path or path == "/":
                return False

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
                "/contact",
                "/about",
                "/account",
                "/subscribe",
                "/newsletter",
                "/videos/",
                "/gallery/",
            )

            if any(part in path for part in blocked_parts):
                return False

            if path.endswith((
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".webp",
                ".svg",
                ".pdf",
                ".zip",
            )):
                return False

            return True

        except Exception:
            return False

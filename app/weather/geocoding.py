"""
KhabarF24 Weather - Geocoding

تبدیل نام شهر به مختصات جغرافیایی با استفاده از
Open-Meteo Geocoding API.
"""

from typing import Any, Dict, List, Optional

import aiohttp

from app.utils.logger import logger


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)


class GeocodingClient:
    """Client برای Open-Meteo Geocoding API."""

    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    async def search(
        self,
        city: str,
        count: int = 5,
        language: str = "fa",
        country_code: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        جست‌وجوی شهر.

        Args:
            city:
                نام شهر.

            count:
                تعداد نتایج موردنظر.

            language:
                زبان نام شهر و کشور.

            country_code:
                کد کشور دو حرفی ISO در صورت نیاز.

        Returns:
            لیستی از مکان‌های پیدا شده.
        """

        if not city or not city.strip():
            return []

        params = {
            "name": city.strip(),
            "count": max(1, min(count, 10)),
            "language": language.lower(),
            "format": "json",
        }

        if country_code:
            params["countryCode"] = (
                country_code.strip().upper()
            )

        timeout = aiohttp.ClientTimeout(
            total=self.timeout
        )

        try:
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:

                async with session.get(
                    GEOCODING_URL,
                    params=params,
                ) as response:

                    if response.status != 200:
                        logger.warning(
                            "Geocoding: HTTP %s برای شهر %s",
                            response.status,
                            city,
                        )
                        return []

                    data = await response.json()

                    if not isinstance(data, dict):
                        logger.warning(
                            "Geocoding: پاسخ نامعتبر برای %s",
                            city,
                        )
                        return []

                    results = data.get(
                        "results",
                        []
                    )

                    if not isinstance(results, list):
                        return []

                    return results

        except aiohttp.ClientError as e:
            logger.warning(
                "Geocoding: خطای ارتباطی برای %s -> %s",
                city,
                e,
            )

        except TimeoutError:
            logger.warning(
                "Geocoding: timeout برای شهر %s",
                city,
            )

        except Exception as e:
            logger.warning(
                "Geocoding: خطای غیرمنتظره -> %s",
                e,
            )

        return []

    async def get_city(
        self,
        city: str,
        language: str = "fa",
        country_code: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        بهترین نتیجه برای یک شهر را برمی‌گرداند.

        اگر شهری پیدا نشود None برمی‌گرداند.
        """

        results = await self.search(
            city=city,
            count=5,
            language=language,
            country_code=country_code,
        )

        if not results:
            return None

        return self._normalize_result(
            results[0]
        )

    @staticmethod
    def _normalize_result(
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        داده خام Open-Meteo را به ساختار ساده‌تر
        و قابل استفاده در WeatherService تبدیل می‌کند.
        """

        return {
            "id": result.get("id"),

            "name": result.get(
                "name"
            ),

            "latitude": result.get(
                "latitude"
            ),

            "longitude": result.get(
                "longitude"
            ),

            "elevation": result.get(
                "elevation"
            ),

            "timezone": result.get(
                "timezone"
            ),

            "country_code": result.get(
                "country_code"
            ),

            "country": result.get(
                "country"
            ),

            "admin1": result.get(
                "admin1"
            ),

            "admin2": result.get(
                "admin2"
            ),

            "population": result.get(
                "population"
            ),

            "feature_code": result.get(
                "feature_code"
            ),
  }

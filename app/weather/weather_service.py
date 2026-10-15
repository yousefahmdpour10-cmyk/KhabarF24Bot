"""
KhabarF24 Weather Service

تبدیل داده خام Open-Meteo به ساختار مرتب و قابل استفاده
برای Formatter و سیستم هواشناسی KhabarF24.
"""

from typing import Any, Dict, List, Optional

from app.weather.open_meteo import OpenMeteoClient
from app.weather.weather_codes import (
    get_weather_description,
    get_weather_icon,
)
from app.utils.logger import logger


class WeatherService:
    """منطق اصلی دریافت و پردازش اطلاعات هواشناسی."""

    def __init__(
        self,
        client: Optional[OpenMeteoClient] = None,
    ):
        self.client = client or OpenMeteoClient()

    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> Optional[Dict[str, Any]]:
        """
        دریافت و پردازش وضعیت هوا.

        خروجی شامل:
        - وضعیت فعلی
        - اطلاعات روزانه
        - پیش‌بینی ساعتی
        - مختصات
        - منطقه زمانی
        """

        data = await self.client.get_weather(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
        )

        if not data:
            logger.warning(
                "WeatherService: داده‌ای از Open-Meteo دریافت نشد."
            )
            return None

        try:
            return self._parse_weather_data(data)

        except Exception as e:
            logger.warning(
                f"WeatherService: خطا در پردازش داده‌ها -> {e}"
            )
            return None

    # ========================================================
    # پردازش کلی
    # ========================================================

    def _parse_weather_data(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        current = self._parse_current(
            data.get("current", {})
        )

        daily = self._parse_daily(
            data.get("daily", {})
        )

        hourly = self._parse_hourly(
            data.get("hourly", {})
        )

        return {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "timezone": data.get("timezone"),
            "timezone_abbreviation": data.get(
                "timezone_abbreviation"
            ),
            "elevation": data.get("elevation"),
            "current": current,
            "daily": daily,
            "hourly": hourly,
        }

    # ========================================================
    # وضعیت فعلی
    # ========================================================

    def _parse_current(
        self,
        current: Dict[str, Any],
    ) -> Dict[str, Any]:

        weather_code = current.get(
            "weather_code"
        )

        return {
            "time": current.get("time"),

            "temperature": current.get(
                "temperature_2m"
            ),

            "apparent_temperature": current.get(
                "apparent_temperature"
            ),

            "humidity": current.get(
                "relative_humidity_2m"
            ),

            "is_day": current.get(
                "is_day"
            ),

            "precipitation": current.get(
                "precipitation"
            ),

            "rain": current.get(
                "rain"
            ),

            "cloud_cover": current.get(
                "cloud_cover"
            ),

            "pressure": current.get(
                "pressure_msl"
            ),

            "wind_speed": current.get(
                "wind_speed_10m"
            ),

            "wind_direction": current.get(
                "wind_direction_10m"
            ),

            "weather_code": weather_code,

            "icon": get_weather_icon(
                weather_code
            ),

            "description": get_weather_description(
                weather_code
            ),
        }

    # ========================================================
    # پیش‌بینی روزانه
    # ========================================================

    def _parse_daily(
        self,
        daily: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        if not daily:
            return []

        dates = daily.get(
            "time",
            []
        )

        weather_codes = daily.get(
            "weather_code",
            []
        )

        max_temperatures = daily.get(
            "temperature_2m_max",
            []
        )

        min_temperatures = daily.get(
            "temperature_2m_min",
            []
        )

        apparent_max = daily.get(
            "apparent_temperature_max",
            []
        )

        apparent_min = daily.get(
            "apparent_temperature_min",
            []
        )

        sunrise = daily.get(
            "sunrise",
            []
        )

        sunset = daily.get(
            "sunset",
            []
        )

        precipitation = daily.get(
            "precipitation_sum",
            []
        )

        rain = daily.get(
            "rain_sum",
            []
        )

        precipitation_probability = daily.get(
            "precipitation_probability_max",
            []
        )

        wind_speed = daily.get(
            "wind_speed_10m_max",
            []
        )

        wind_direction = daily.get(
            "wind_direction_10m_dominant",
            []
        )

        result = []

        for index, date in enumerate(dates):

            code = self._get_index(
                weather_codes,
                index
            )

            result.append(
                {
                    "date": date,

                    "weather_code": code,

                    "icon": get_weather_icon(
                        code
                    ),

                    "description": (
                        get_weather_description(
                            code
                        )
                    ),

                    "temperature_max": (
                        self._get_index(
                            max_temperatures,
                            index
                        )
                    ),

                    "temperature_min": (
                        self._get_index(
                            min_temperatures,
                            index
                        )
                    ),

                    "apparent_temperature_max": (
                        self._get_index(
                            apparent_max,
                            index
                        )
                    ),

                    "apparent_temperature_min": (
                        self._get_index(
                            apparent_min,
                            index
                        )
                    ),

                    "sunrise": (
                        self._get_index(
                            sunrise,
                            index
                        )
                    ),

                    "sunset": (
                        self._get_index(
                            sunset,
                            index
                        )
                    ),

                    "precipitation": (
                        self._get_index(
                            precipitation,
                            index
                        )
                    ),

                    "rain": (
                        self._get_index(
                            rain,
                            index
                        )
                    ),

                    "precipitation_probability": (
                        self._get_index(
                            precipitation_probability,
                            index
                        )
                    ),

                    "wind_speed": (
                        self._get_index(
                            wind_speed,
                            index
                        )
                    ),

                    "wind_direction": (
                        self._get_index(
                            wind_direction,
                            index
                        )
                    ),
                }
            )

        return result

    # ========================================================
    # پیش‌بینی ساعتی
    # ========================================================

    def _parse_hourly(
        self,
        hourly: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        if not hourly:
            return []

        times = hourly.get(
            "time",
            []
        )

        temperatures = hourly.get(
            "temperature_2m",
            []
        )

        apparent_temperatures = hourly.get(
            "apparent_temperature",
            []
        )

        precipitation_probability = hourly.get(
            "precipitation_probability",
            []
        )

        precipitation = hourly.get(
            "precipitation",
            []
        )

        weather_codes = hourly.get(
            "weather_code",
            []
        )

        wind_speed = hourly.get(
            "wind_speed_10m",
            []
        )

        result = []

        for index, time in enumerate(times):

            code = self._get_index(
                weather_codes,
                index
            )

            result.append(
                {
                    "time": time,

                    "temperature": (
                        self._get_index(
                            temperatures,
                            index
                        )
                    ),

                    "apparent_temperature": (
                        self._get_index(
                            apparent_temperatures,
                            index
                        )
                    ),

                    "precipitation_probability": (
                        self._get_index(
                            precipitation_probability,
                            index
                        )
                    ),

                    "precipitation": (
                        self._get_index(
                            precipitation,
                            index
                        )
                    ),

                    "weather_code": code,

                    "icon": get_weather_icon(
                        code
                    ),

                    "description": (
                        get_weather_description(
                            code
                        )
                    ),

                    "wind_speed": (
                        self._get_index(
                            wind_speed,
                            index
                        )
                    ),
                }
            )

        return result

    # ========================================================
    # ابزار کمکی
    # ========================================================

    @staticmethod
    def _get_index(
        values: List[Any],
        index: int,
        default: Any = None,
    ) -> Any:
        """
        دریافت امن مقدار از لیست.

        اگر API برای یک فیلد مقدار کمتری برگرداند،
        برنامه Crash نمی‌کند.
        """

        if index < 0:
            return default

        if index >= len(values):
            return default

        return values[index]

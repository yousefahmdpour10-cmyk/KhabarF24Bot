"""
Smart Formatter Manager
"""

from app.models.raw_news import RawNews

from app.formatter.templates.world import WorldTemplate
from app.formatter.templates.iran import IranTemplate
from app.formatter.templates.politics import PoliticsTemplate
from app.formatter.templates.economy import EconomyTemplate
from app.formatter.templates.technology import TechnologyTemplate
from app.formatter.templates.health import HealthTemplate
from app.formatter.templates.sport import SportTemplate
from app.formatter.templates.weather import WeatherTemplate


class Formatter:

    def __init__(self):
        self.templates = {
            "world": WorldTemplate(),
            "iran": IranTemplate(),
            "politics": PoliticsTemplate(),
            "economy": EconomyTemplate(),
            "technology": TechnologyTemplate(),
            "health": HealthTemplate(),
            "sport": SportTemplate(),
            "weather": WeatherTemplate(),
        }

    async def format(
        self,
        news: RawNews,
    ) -> str:

        category = getattr(
            news,
            "category",
            "world",
        )

        template = self.templates.get(
            category,
            WorldTemplate(),
        )

        return await template.format(news)

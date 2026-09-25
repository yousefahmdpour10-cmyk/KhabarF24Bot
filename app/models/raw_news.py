"""
مدل خبر خام

تمام خبرهایی که از RSS، سایت، API یا شبکه‌های اجتماعی دریافت می‌شوند
ابتدا به صورت RawNews وارد سیستم خواهند شد.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class RawNews:
    """
    مدل مرکزی خبر خام و داده‌های استخراج‌شده از آن.
    """

    # ============================================================
    # اطلاعات اصلی خبر
    # ============================================================

    id: Optional[str] = None

    title: str = ""

    content: str = ""

    summary: str = ""

    url: str = ""

    image_url: str = ""

    author: str = ""

    published_at: Optional[datetime] = None

    fetched_at: datetime = field(
        default_factory=datetime.utcnow
    )

    source: str = ""

    source_id: str = ""

    country: str = ""

    language: str = ""

    category: str = ""

    tags: List[str] = field(
        default_factory=list
    )

    related_urls: List[str] = field(
        default_factory=list
    )

    raw_data: dict = field(
        default_factory=dict
    )

    # ============================================================
    # Entity Data
    # ============================================================

    teams: List[str] = field(
        default_factory=list
    )

    people: List[dict] = field(
        default_factory=list
    )

    leagues: List[str] = field(
        default_factory=list
    )

    tournaments: List[str] = field(
        default_factory=list
    )

    stadiums: List[str] = field(
        default_factory=list
    )

    referees: List[str] = field(
        default_factory=list
    )

    # ============================================================
    # Football Match Data
    # ============================================================

    match_date: Optional[str] = None

    match_time: Optional[str] = None

    stage: str = ""

    home_team: str = ""

    away_team: str = ""

    # ============================================================
    # Lineup
    # ============================================================

    lineup: dict = field(
        default_factory=dict
    )

    # ============================================================
    # Match Result
    # ============================================================

    home_score: Optional[int] = None

    away_score: Optional[int] = None

    result_status: str = ""

    # ============================================================
    # Goals / Assists
    # ============================================================

    goals: List[dict] = field(
        default_factory=list
    )

    assists: List[dict] = field(
        default_factory=list
    )

    # ============================================================
    # Cards
    # ============================================================

    yellow_cards: List[dict] = field(
        default_factory=list
    )

    red_cards: List[dict] = field(
        default_factory=list
    )

    # ============================================================
    # Coaches / Captains
    # ============================================================

    coaches: List[dict] = field(
        default_factory=list
    )

    captains: List[dict] = field(
        default_factory=list
    )

    # ============================================================
    # Interviews
    # ============================================================

    interviews: List[dict] = field(
        default_factory=list
    )

    # ============================================================
    # Match Statistics
    # ============================================================

    statistics: dict = field(
        default_factory=dict
    )

    # ============================================================
    # Transfer
    # ============================================================

    transfer: dict = field(
        default_factory=dict
    )

"""
Basketball Builder
KhabarF24

لایه اتصال اطلاعات تشخیص داده‌شده بسکتبال
به Formatter.

این فایل:
    - اطلاعات موجود در raw_data را می‌خواند
    - در صورت نبود اطلاعات، از Basketball Detector استفاده می‌کند
    - اطلاعات بسکتبال را به بخش‌های قابل نمایش تبدیل می‌کند

این فایل مسئول ساخت Header/Footer اصلی تلگرام نیست.
"""

from typing import Any, Dict, List, Optional

from app.models.raw_news import RawNews

from .detector import (
    detect_basketball_from_parts,
)


class BasketballBuilder:
    """
    Builder اطلاعات اختصاصی بسکتبال.
    """

    def build(
        self,
        news: RawNews,
    ) -> str:
        """
        ساخت بخش تخصصی خبر بسکتبال.
        """

        data = self._data(news)

        # ----------------------------------------------------
        # DETECTION
        # ----------------------------------------------------

        detection = detect_basketball_from_parts(
            title=getattr(news, "title", ""),
            summary=getattr(news, "summary", ""),
            content=getattr(news, "content", ""),
        )

        sections: List[str] = []

        # ====================================================
        # LEAGUE
        # ====================================================

        league = (
            self._clean(data.get("league"))
            or detection.league
        )

        if league:
            sections.append(
                f"🏆 لیگ: {league}"
            )

        # ====================================================
        # TOURNAMENT
        # ====================================================

        tournament = (
            self._clean(data.get("tournament"))
            or detection.tournament
        )

        if tournament:
            sections.append(
                f"🏆 تورنمنت: {tournament}"
            )

        # ====================================================
        # MATCH
        # ====================================================

        match = self.get_match(
            news,
            detection.teams,
        )

        if match:
            sections.append(
                f"🏀 {match}"
            )

        # ====================================================
        # RESULT
        # ====================================================

        result = self.get_result(
            news,
            detection.score,
        )

        if result:
            sections.append(
                f"🏁 نتیجه: {result}"
            )

        # ====================================================
        # ARENA
        # ====================================================

        arena = self.get_arena(news)

        if arena:
            sections.append(
                f"🏟️ {arena}"
            )

        # ====================================================
        # DATE / TIME
        # ====================================================

        match_time = self.get_match_time(news)

        if match_time:
            sections.append(
                f"⏰ {match_time}"
            )

        # ====================================================
        # LINEUP
        # ====================================================

        lineup = self.get_lineup(news)

        if lineup:
            sections.append(
                f"👥 ترکیب:\n{lineup}"
            )

        # ====================================================
        # COACH
        # ====================================================

        coach = self.get_coach(news)

        if coach:
            sections.append(
                f"👔 سرمربی: {coach}"
            )

        # ====================================================
        # CAPTAIN
        # ====================================================

        captain = self.get_captain(news)

        if captain:
            sections.append(
                f"©️ کاپیتان: {captain}"
            )

        # ====================================================
        # REFEREES
        # ====================================================

        referees = self.get_referees(news)

        if referees:
            sections.append(
                f"👨‍⚖️ داوران: {referees}"
            )

        # ====================================================
        # QUARTERS
        # ====================================================

        quarters = self.get_quarters(news)

        if quarters:
            sections.append(
                f"⏱️ کوارترها:\n{quarters}"
            )

        # ====================================================
        # STATS
        # ====================================================

        stats = self.get_stats(news)

        if stats:
            sections.append(
                f"📊 آمار:\n{stats}"
            )

        # ====================================================
        # PLAYERS
        # ====================================================

        players = self.get_players(
            news,
            detection.players,
        )

        if players:
            sections.append(
                f"🏀 بازیکنان:\n{players}"
            )

        # ====================================================
        # POINTS
        # ====================================================

        points = self.get_points(news)

        if points:
            sections.append(
                f"🎯 امتیاز: {points}"
            )

        # ====================================================
        # ASSISTS
        # ====================================================

        assists = self.get_assists(news)

        if assists:
            sections.append(
                f"🅰️ پاس گل: {assists}"
            )

        # ====================================================
        # REBOUNDS
        # ====================================================

        rebounds = self.get_rebounds(news)

        if rebounds:
            sections.append(
                f"🔄 ریباند: {rebounds}"
            )

        # ====================================================
        # FOULS
        # ====================================================

        fouls = self.get_fouls(news)

        if fouls:
            sections.append(
                f"🚫 خطا: {fouls}"
            )

        # ====================================================
        # PRE-MATCH INTERVIEW
        # ====================================================

        pre_interview = (
            self.get_pre_match_interview(news)
        )

        if pre_interview:
            sections.append(
                f"🎙️ مصاحبه قبل از بازی:\n"
                f"{pre_interview}"
            )

        # ====================================================
        # POST-MATCH INTERVIEW
        # ====================================================

        post_interview = (
            self.get_post_match_interview(news)
        )

        if post_interview:
            sections.append(
                f"🎙️ مصاحبه بعد از بازی:\n"
                f"{post_interview}"
            )

        # ====================================================
        # TRANSFER
        # ====================================================

        transfer = self.get_transfer(news)

        if transfer:
            sections.append(
                f"🔄 نقل‌وانتقال: {transfer}"
            )

        return "\n\n".join(
            sections
        )

    # ========================================================
    # DATA
    # ========================================================

    @staticmethod
    def _data(
        news: RawNews,
    ) -> Dict[str, Any]:

        raw_data = getattr(
            news,
            "raw_data",
            None,
        )

        if isinstance(raw_data, dict):
            return raw_data

        return {}

    # ========================================================
    # MATCH
    # ========================================================

    def get_match(
        self,
        news: RawNews,
        detected_teams: Optional[List[str]] = None,
    ) -> Optional[str]:

        data = self._data(news)

        home = self._clean(
            data.get("home_team")
        )

        away = self._clean(
            data.get("away_team")
        )

        if not home and detected_teams:
            if len(detected_teams) >= 1:
                home = detected_teams[0]

        if not away and detected_teams:
            if len(detected_teams) >= 2:
                away = detected_teams[1]

        if not home or not away:
            return None

        return (
            f"{home} 🆚 {away}"
        )

    # ========================================================
    # RESULT
    # ========================================================

    def get_result(
        self,
        news: RawNews,
        detected_score: Any = None,
    ) -> Optional[str]:

        data = self._data(news)

        value = self._clean(
            data.get("result")
        )

        if value:
            return value

        if (
            detected_score
            and getattr(
                detected_score,
                "is_detected",
                False,
            )
        ):

            home_score = getattr(
                detected_score,
                "home_score",
                None,
            )

            away_score = getattr(
                detected_score,
                "away_score",
                None,
            )

            if (
                home_score is not None
                and away_score is not None
            ):
                return (
                    f"{home_score} - "
                    f"{away_score}"
                )

        return None

    # ========================================================
    # ARENA
    # ========================================================

    def get_arena(
        self,
        news: RawNews,
    ) -> Optional[str]:

        data = self._data(news)

        value = data.get("arena")

        if not value:
            value = data.get(
                "stadium"
            )

        if not value:
            value = data.get(
                "venue"
            )

        return self._clean(value)

    # ========================================================
    # MATCH TIME
    # ========================================================

    def get_match_time(
        self,
        news: RawNews,
    ) -> Optional[str]:

        data = self._data(news)

        value = data.get(
            "match_time"
        )

        if not value:
            value = data.get(
                "date_time"
            )

        if not value:
            value = data.get(
                "scheduled_at"
            )

        return self._clean(value)

    # ========================================================
    # LINEUP
    # ========================================================

    def get_lineup(
        self,
        news: RawNews,
    ) -> Optional[str]:

        data = self._data(news)

        lineup = data.get(
            "lineup"
        )

        if not lineup:
            lineup = data.get(
                "starting_five"
            )

        if isinstance(
            lineup,
            dict,
        ):

            lines = []

            for team, players in (
                lineup.items()
            ):

                if isinstance(
                    players,
                    list,
                ):

                    names = "، ".join(
                        str(player)
                        for player in players
                        if player
                    )

                    if names:
                        lines.append(
                            f"{team}: {names}"
                        )

                elif players:

                    lines.append(
                        f"{team}: {players}"
                    )

            if lines:
                return "\n".join(lines)

        if isinstance(
            lineup,
            list,
        ):

            return "\n".join(
                str(player)
                for player in lineup
                if player
            )

        return self._clean(
            lineup
        )

    # ========================================================
    # COACH
    # ========================================================

    def get_coach(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("coach")

        return self._clean(value)

    # ========================================================
    # CAPTAIN
    # ========================================================

    def get_captain(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("captain")

        return self._clean(value)

    # ========================================================
    # REFEREES
    # ========================================================

    def get_referees(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("referees")

        if isinstance(
            value,
            list,
        ):

            return "، ".join(
                str(referee)
                for referee in value
                if referee
            )

        return self._clean(value)

    # ========================================================
    # QUARTERS
    # ========================================================

    def get_quarters(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("quarters")

        if isinstance(
            value,
            dict,
        ):

            ordered = []

            for quarter in (
                "Q1",
                "Q2",
                "Q3",
                "Q4",
            ):

                if quarter in value:

                    ordered.append(
                        f"{quarter}: "
                        f"{value[quarter]}"
                    )

            if ordered:
                return "\n".join(
                    ordered
                )

        if isinstance(
            value,
            list,
        ):

            return "\n".join(
                str(item)
                for item in value
                if item
            )

        return self._clean(
            value
        )

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("stats")

        if isinstance(
            value,
            dict,
        ):

            lines = []

            for key, item in (
                value.items()
            ):

                if item is None:
                    continue

                lines.append(
                    f"{key}: {item}"
                )

            if lines:
                return "\n".join(
                    lines
                )

        if isinstance(
            value,
            list,
        ):

            return "\n".join(
                str(item)
                for item in value
                if item
            )

        return self._clean(
            value
        )

    # ========================================================
    # PLAYERS
    # ========================================================

    def get_players(
        self,
        news: RawNews,
        detected_players: Optional[List[str]] = None,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("players")

        if isinstance(
            value,
            list,
        ):

            return "\n".join(
                str(player)
                for player in value
                if player
            )

        cleaned = self._clean(
            value
        )

        if cleaned:
            return cleaned

        if detected_players:
            return "\n".join(
                detected_players
            )

        return None

    # ========================================================
    # POINTS
    # ========================================================

    def get_points(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("points")

        return self._clean(value)

    # ========================================================
    # ASSISTS
    # ========================================================

    def get_assists(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("assists")

        return self._clean(value)

    # ========================================================
    # REBOUNDS
    # ========================================================

    def get_rebounds(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("rebounds")

        return self._clean(value)

    # ========================================================
    # FOULS
    # ========================================================

    def get_fouls(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("fouls")

        return self._clean(value)

    # ========================================================
    # PRE-MATCH INTERVIEW
    # ========================================================

    def get_pre_match_interview(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get(
            "pre_match_interview"
        )

        return self._clean(value)

    # ========================================================
    # POST-MATCH INTERVIEW
    # ========================================================

    def get_post_match_interview(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get(
            "post_match_interview"
        )

        return self._clean(value)

    # ========================================================
    # TRANSFER
    # ========================================================

    def get_transfer(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(
            news
        ).get("transfer")

        return self._clean(value)

    # ========================================================
    # CLEAN
    # ========================================================

    @staticmethod
    def _clean(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        if isinstance(
            value,
            str,
        ):

            value = value.strip()

            if not value:
                return None

            return value

        return str(value)

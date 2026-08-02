"""
Basketball Builder
KhabarF24

جمع‌آوری و آماده‌سازی اطلاعات اختصاصی اخبار بسکتبال.

این فایل مسئول ساخت متن نهایی تلگرام نیست.
وظیفه آن فقط استخراج و مرتب‌سازی اطلاعات بسکتبال
از RawNews است تا Formatter بتواند از آن استفاده کند.
"""

from typing import Any, Dict, List, Optional

from app.models.raw_news import RawNews


class BasketballBuilder:
    """
    Builder اطلاعات بسکتبال.
    """

    def build(
        self,
        news: RawNews,
    ) -> str:
        """
        تمام اطلاعات قابل استفاده خبر بسکتبال را
        جمع‌آوری و به متن قابل نمایش تبدیل می‌کند.
        """

        data = news.raw_data or {}

        sections: List[str] = []

        # ====================================================
        # LEAGUE
        # ====================================================

        league = self.get_league(news)

        if league:
            sections.append(
                f"🏆 {league}"
            )

        # ====================================================
        # TOURNAMENT
        # ====================================================

        tournament = self.get_tournament(news)

        if tournament:
            sections.append(
                f"🏆 {tournament}"
            )

        # ====================================================
        # MATCH
        # ====================================================

        match = self.get_match(news)

        if match:
            sections.append(
                f"🏀 {match}"
            )

        # ====================================================
        # RESULT
        # ====================================================

        result = self.get_result(news)

        if result:
            sections.append(
                f"🏁 {result}"
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
        # LINEUP / STARTING FIVE
        # ====================================================

        lineup = self.get_lineup(news)

        if lineup:
            sections.append(
                f"👥\n{lineup}"
            )

        # ====================================================
        # COACH
        # ====================================================

        coach = self.get_coach(news)

        if coach:
            sections.append(
                f"👔 {coach}"
            )

        # ====================================================
        # CAPTAIN
        # ====================================================

        captain = self.get_captain(news)

        if captain:
            sections.append(
                f"©️ {captain}"
            )

        # ====================================================
        # REFEREES
        # ====================================================

        referees = self.get_referees(news)

        if referees:
            sections.append(
                f"👨‍⚖️ {referees}"
            )

        # ====================================================
        # QUARTERS
        # ====================================================

        quarters = self.get_quarters(news)

        if quarters:
            sections.append(
                f"⏱️\n{quarters}"
            )

        # ====================================================
        # STATS
        # ====================================================

        stats = self.get_stats(news)

        if stats:
            sections.append(
                f"📊\n{stats}"
            )

        # ====================================================
        # TOP PLAYERS
        # ====================================================

        players = self.get_players(news)

        if players:
            sections.append(
                f"🏀\n{players}"
            )

        # ====================================================
        # POINTS
        # ====================================================

        points = self.get_points(news)

        if points:
            sections.append(
                f"🎯 {points}"
            )

        # ====================================================
        # ASSISTS
        # ====================================================

        assists = self.get_assists(news)

        if assists:
            sections.append(
                f"🅰️ {assists}"
            )

        # ====================================================
        # REBOUNDS
        # ====================================================

        rebounds = self.get_rebounds(news)

        if rebounds:
            sections.append(
                f"🔄 {rebounds}"
            )

        # ====================================================
        # FOULS
        # ====================================================

        fouls = self.get_fouls(news)

        if fouls:
            sections.append(
                f"🚫 {fouls}"
            )

        # ====================================================
        # PRE-MATCH INTERVIEW
        # ====================================================

        pre_interview = self.get_pre_match_interview(news)

        if pre_interview:
            sections.append(
                f"🎙️\n{pre_interview}"
            )

        # ====================================================
        # POST-MATCH INTERVIEW
        # ====================================================

        post_interview = self.get_post_match_interview(news)

        if post_interview:
            sections.append(
                f"🎙️\n{post_interview}"
            )

        # ====================================================
        # TRANSFER
        # ====================================================

        transfer = self.get_transfer(news)

        if transfer:
            sections.append(
                f"🔄 {transfer}"
            )

        return "\n\n".join(sections)

    # ========================================================
    # DATA ACCESS
    # ========================================================

    @staticmethod
    def _data(
        news: RawNews,
    ) -> Dict[str, Any]:

        return news.raw_data or {}

    # ========================================================
    # LEAGUE
    # ========================================================

    def get_league(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("league")

        return self._clean(value)

    # ========================================================
    # TOURNAMENT
    # ========================================================

    def get_tournament(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("tournament")

        return self._clean(value)

    # ========================================================
    # MATCH
    # ========================================================

    def get_match(
        self,
        news: RawNews,
    ) -> Optional[str]:

        data = self._data(news)

        home = self._clean(
            data.get("home_team")
        )

        away = self._clean(
            data.get("away_team")
        )

        if not home or not away:
            return None

        return f"{home} 🆚 {away}"

    # ========================================================
    # RESULT
    # ========================================================

    def get_result(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("result")

        return self._clean(value)

    # ========================================================
    # ARENA
    # ========================================================

    def get_arena(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("arena")

        if not value:
            value = self._data(news).get(
                "stadium"
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

        value = data.get("match_time")

        if not value:
            value = data.get("date_time")

        return self._clean(value)

    # ========================================================
    # LINEUP
    # ========================================================

    def get_lineup(
        self,
        news: RawNews,
    ) -> Optional[str]:

        data = self._data(news)

        lineup = data.get("lineup")

        if not lineup:
            lineup = data.get(
                "starting_five"
            )

        if isinstance(lineup, list):
            return "\n".join(
                str(player)
                for player in lineup
                if player
            )

        return self._clean(lineup)

    # ========================================================
    # COACH
    # ========================================================

    def get_coach(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("coach")

        return self._clean(value)

    # ========================================================
    # CAPTAIN
    # ========================================================

    def get_captain(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get("captain")

        return self._clean(value)

    # ========================================================
    # REFEREES
    # ========================================================

    def get_referees(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "referees"
        )

        if isinstance(value, list):
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

        value = self._data(news).get(
            "quarters"
        )

        if isinstance(value, dict):

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

        if isinstance(value, list):

            return "\n".join(
                str(item)
                for item in value
                if item
            )

        return self._clean(value)

    # ========================================================
    # STATS
    # ========================================================

    def get_stats(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "stats"
        )

        if isinstance(value, dict):

            lines = []

            for key, item in value.items():

                if item is None:
                    continue

                lines.append(
                    f"{key}: {item}"
                )

            if lines:
                return "\n".join(lines)

        if isinstance(value, list):

            return "\n".join(
                str(item)
                for item in value
                if item
            )

        return self._clean(value)

    # ========================================================
    # PLAYERS
    # ========================================================

    def get_players(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "players"
        )

        if isinstance(value, list):

            return "\n".join(
                str(player)
                for player in value
                if player
            )

        return self._clean(value)

    # ========================================================
    # POINTS
    # ========================================================

    def get_points(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "points"
        )

        return self._clean(value)

    # ========================================================
    # ASSISTS
    # ========================================================

    def get_assists(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "assists"
        )

        return self._clean(value)

    # ========================================================
    # REBOUNDS
    # ========================================================

    def get_rebounds(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "rebounds"
        )

        return self._clean(value)

    # ========================================================
    # FOULS
    # ========================================================

    def get_fouls(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
            "fouls"
        )

        return self._clean(value)

    # ========================================================
    # PRE-MATCH INTERVIEW
    # ========================================================

    def get_pre_match_interview(
        self,
        news: RawNews,
    ) -> Optional[str]:

        value = self._data(news).get(
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

        value = self._data(news).get(
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

        value = self._data(news).get(
            "transfer"
        )

        return self._clean(value)

    # ========================================================
    # CLEAN VALUE
    # ========================================================

    @staticmethod
    def _clean(
        value: Any,
    ) -> Optional[str]:

        if value is None:
            return None

        if isinstance(value, str):

            value = value.strip()

            if not value:
                return None

            return value

        return str(value)

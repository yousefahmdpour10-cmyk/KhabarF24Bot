"""
Football Lineup Builder
"""

from app.models.raw_news import RawNews


class LineupBuilder:

    def build(
        self,
        news: RawNews,
    ) -> list[str]:

        lines = []

        lineup = getattr(
            news,
            "lineup",
            None,
        )

        if not lineup:
            return lines

        home = lineup.get(
            "home",
            {},
        )

        away = lineup.get(
            "away",
            {},
        )

        self._build_team(
            lines,
            home,
        )

        self._build_team(
            lines,
            away,
        )

        return lines

    def _build_team(
        self,
        lines: list[str],
        team: dict,
    ) -> None:

        name = team.get(
            "name",
        )

        if not name:
            return

        lines.append(
            f"📋 {name}"
        )

        starters = team.get(
            "starting",
            [],
        )

        if starters:

            for player in starters:

                lines.append(
                    f"👕 {player}"
                )

        substitutes = team.get(
            "substitutes",
            [],
        )

        if substitutes:

            lines.append(
                "🪑 ذخیره"
            )

            for player in substitutes:

                lines.append(
                    f"👕 {player}"
                )

        captain = team.get(
            "captain",
        )

        if captain:

            lines.append(
                f"©️ {captain}"
      )

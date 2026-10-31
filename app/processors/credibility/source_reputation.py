"""
Source Reputation Database

امتیاز اعتبار منابع. دو لایه دارد:

۱) فهرست دستی (SOURCE_REPUTATION_MANUAL): برای منابع شناخته‌شده‌ای که
   می‌خواهیم امتیازشان را خودمان تعیین کنیم.
۲) برای هر منبعی که در فهرست دستی نبود، از فایل‌های data/sources/*.json
   استفاده می‌شود: «priority» هر منبع همان اعتبار آن (۰ تا ۱۰۰) است
   (طبق NewsSource). امتیاز بین ۷۰ تا ۹۷ بریده می‌شود.

بدون لایه‌ی دوم، هر منبعی که اسمش دقیقاً در فهرست دستی نبود امتیاز
پیش‌فرض ۵۰ می‌گرفت و (چون حداقل ۷۰ است) خبرش رد می‌شد.
"""

MIN_DERIVED = 70
MAX_DERIVED = 97

SOURCE_REPUTATION_MANUAL = {

    # منابع خبری بین‌المللی
    "Reuters": 100,
    "AP": 100,
    "AFP": 98,
    "BBC": 96,
    "BBC Business": 94,
    "BBC Top Stories": 96,
    "CNN": 94,
    "Al Jazeera": 92,
    "Guardian": 90,
    "The New York Times": 92,

    # منابع خبری ایران
    "IRNA": 85,
    "ISNA": 84,
    "Tasnim News": 82,
    "Mehr News": 82,
    "Fars": 80,
    "Khabar Online": 78,
    "Tabnak": 75,
    "YJC": 72,

    # منابع ورزشی بین‌المللی
    "BBC Sport": 94,
    "BBC Football": 94,
    "ESPN": 90,
    "ESPN Soccer": 90,
    "Gianluca Di Marzio": 88,
    "Transfermarkt": 85,
    "Fabrizio Romano": 85,
    "Fabrizio Romano Telegram": 85,
    "Sky Sports Football": 90,
    "UEFA": 96,
    "FIFA": 96,
    "Premier League": 96,
    "API-Football": 95,
}


def _normalize(name) -> str:
    return " ".join(
        str(name or "").replace("\u200c", "").casefold().split()
    )


class _ReputationTable(dict):
    """
    دیکشنری اعتبار با لایه‌ی دوم از JSON. مثل یک dict معمولی کار می‌کند:
    .get / [] / in.
    """

    _derived_cache = None
    _load_attempts = 0

    def _derived(self, name):
        if _ReputationTable._derived_cache is None:
            self._load()

        cache = _ReputationTable._derived_cache or {}

        return cache.get(_normalize(name))

    @staticmethod
    def _load() -> None:
        """نام و priority همه‌ی منابع را از JSON می‌خواند (حداکثر ۳ تلاش)."""

        if _ReputationTable._load_attempts >= 3:
            return

        _ReputationTable._load_attempts += 1

        derived = {}

        try:
            from config.sources import load_sources

            for source in load_sources():
                name = getattr(source, "name", "")
                priority = getattr(source, "priority", None)

                if not name or priority is None:
                    continue

                derived[_normalize(name)] = max(
                    MIN_DERIVED,
                    min(MAX_DERIVED, int(priority)),
                )

        except Exception:
            derived = {}

        if derived:
            _ReputationTable._derived_cache = derived

    def __contains__(self, key):
        return dict.__contains__(self, key) or self._derived(key) is not None

    def __getitem__(self, key):
        if dict.__contains__(self, key):
            return dict.__getitem__(self, key)

        value = self._derived(key)

        if value is None:
            raise KeyError(key)

        return value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


SOURCE_REPUTATION = _ReputationTable(SOURCE_REPUTATION_MANUAL)

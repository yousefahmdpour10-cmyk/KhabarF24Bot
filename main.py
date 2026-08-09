"""
KhabarF24 Main Engine
"""

import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import asyncio
from config.settings import CHECK_INTERVAL
from config.sources import load_sources
from app.services.fetch_service import FetchService
from app.processors.pipeline import NewsPipeline
from app.utils.logger import logger

async def main():
    logger.info("🚀 KhabarF24 Bot Started Successfully")

    fetch_service = FetchService()
    pipeline = NewsPipeline()
    sources = load_sources()

    logger.info(f"Loaded {len(sources)} sources")

    while True:
        try:
            logger.info("🔄 Checking for new news...")
            all_news = await fetch_service.fetch_all(sources)

            if all_news:
                for news in all_news[:3]:  # فعلاً حداکثر ۳ خبر در هر چرخه
                    await pipeline.process(news)
                    await asyncio.sleep(5)

            await asyncio.sleep(CHECK_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Error: {e}", exc_info=True)
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())


مسیر پروژه را تحلیل کرد و مشکل import را شناسایی کرد
مسیر پروژه را تحلیل کرد و مشکل import را شناسایی کرد
main.py خودش مشکلی نداره — مسیرها درست تنظیم شدن.

با این حساب، فکر می‌کنم فایل language/detector.py واقعاً رو گیت‌هاب هست ولی یه‌جایی قبل از رسیدن به Railway (توی build) حذف/نادیده گرفته میشه. محتمل‌ترین مقصر: یه فایل مثل .gitignore یا .dockerignore که این پوشه رو مستثنی کرده.

می‌تونی محتوای .gitignore رو بفرستی؟ (تو ریشه‌ی پروژه، کنار main.py)

.env
__pycache__/
*.pyc


Investigated module import obstruction and git configuration anomalies
Investigated module import obstruction and git configuration anomalies
.gitignore مشکلی نداره، این پوشه رو مستثنی نمی‌کنه.

یه احتمال دیگه‌ی قوی: اگه پروژه یه Dockerfile سفارشی داره (به‌جای اینکه Railway خودش با Nixpacks بسازتش)، ممکنه اون Dockerfile به‌جای کپی‌کردن کل پروژه، فقط فایل‌ها/پوشه‌های خاصی رو صریحاً COPY کنه — و چون پوشه‌ی language بعد از نوشتن اون Dockerfile اضافه شده، جا مونده باشه.

می‌تونی بگی آیا تو ریشه‌ی پروژه یه فایل به اسم Dockerfile هست؟ اگه هست، محتواش رو بفرست.

فهمیدم، پس هنوز category و sport باقی مونده. همون روش رو براشون تکرار کن:

تأیید نهایی با کدسپیس
برای اطمینان کامل، تو کدسپیس این دستور رو بزن: ls -la app/processors/ | cat -A هر سه تا پوشه (language, category, sport) باید بلافاصله قبل از $ بیاد، بدون فاصله‌ی اضافی.
1
2
3
وقتی هر سه‌تا درست شد، main.py رو هم از خطوط DEBUG پاک کن و push کن، بعد لاگ دیپلوی جدید رو بفرست.

فاصله شون رو درست کردم حالا چی

این دیف فقط نمایش همون چیزهایی هست که خودم قبلاً ثبت کرده بودم، چیز جدیدی از بیرون نیومده — ادامه می‌دیم.

عالی! حالا دو تا کار مونده:

خطوط DEBUG رو از main.py پاک کن
برو به main.py (روی کدسپیس یا مستقیم گیت‌هاب)، و این بخش رو پاک کن: # --- DEBUG موقت: ... import os print(...) print(...) if ...: print(...) # --- پایان DEBUG --- فقط همین چندخط رو پاک کن، بقیه کد دست نخورد.
1
2
این‌بار امیدوارم لاگ به‌جای ModuleNotFoundError، چیزی شبیه 🚀 KhabarF24 Bot Started Successfully و Loaded N sources نشون بده. نتیجه رو بفرست.








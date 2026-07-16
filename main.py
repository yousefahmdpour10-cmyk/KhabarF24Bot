"""
KhabarF24 Main Engine v6.2

Pipeline:

RSS Fetcher
      ↓
Category Engine
      ↓
AI Processor
      ↓
Sport Engine
      ↓
Quality Engine
      ↓
Importance Engine
      ↓
Formatter
      ↓
Telegram
"""


import asyncio


from news_fetcher import get_latest_news


from telegram_bot import send_message


from news_db import (
    init_db,
    is_published,
    mark_as_published,
)


from category_engine import detect_smart_category


from formatter import format_news


from ai_processor import process_news


from quality_engine import is_high_quality


from importance_engine import is_important


from sport_formatter import format_sport_news







CHECK_INTERVAL = 300







async def check_news():


    news = get_latest_news()



    if not news:


        print("No news found.")

        return





    for item in news:



        link = item.get("link")



        if not link:

            continue





        if is_published(link):

            continue







        raw_title = item.get(
            "title",
            ""
        )


        raw_summary = item.get(
            "summary",
            ""
        )



        category = detect_smart_category(


            title=raw_title,


            summary=raw_summary,


            source=item.get(
                "source",
                ""
            )

        )



        print(
            f"📂 Category: {category}"
        )








        processed = process_news(


            raw_title,


            raw_summary

        )



        title = processed.get(
            "title",
            ""
        )


        summary = processed.get(
            "summary",
            ""
        )







        sport_data = None




        # =====================
        # Sport Processing
        # =====================


        if category == "sport":



            sport_result = format_sport_news(


                title,

                summary

            )



            if sport_result.get(
                "blocked"
            ):


                print(
                    "❌ Sport video-only skipped"
                )


                continue




            title = sport_result.get(

                "title",

                title

            )


            summary = sport_result.get(

                "summary",

                summary

            )



            sport_data = sport_result.get(

                "sport"

            )









        # =====================
        # Quality
        # =====================


        if not is_high_quality(


            title,

            summary

        ):


            print(
                "❌ Low quality news skipped"
            )

            continue








        # =====================
        # Importance
        # =====================


        if not is_important(


            title,

            summary,

            category

        ):


            print(
                "❌ Low importance news skipped"
            )

            continue







        # =====================
        # Formatter
        # =====================


        message = format_news(


            title=title,


            summary=summary,


            source=item.get(
                "source",
                ""
            ),


            category=category,


            sport=sport_data


        )









        await send_message(

            message

        )





        mark_as_published(

            link

        )



        print(
            "✅ News published"
        )




        break










async def main():


    init_db()



    print(
        "🚀 KhabarF24 Started v6.2"
    )



    while True:


        try:


            await check_news()



        except Exception as e:


            print(
                f"Error: {e}"
            )



        await asyncio.sleep(

            CHECK_INTERVAL

        )









if __name__ == "__main__":


    asyncio.run(

        main()

    )

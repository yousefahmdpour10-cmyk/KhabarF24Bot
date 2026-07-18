"""
KhabarF24 Main Engine v7.0

Pipeline:

News Fetcher
      ↓
Category Engine
      ↓
AI Processor
      ↓
Sport Formatter
      ↓
Game Formatter
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
import random



from news_fetcher import get_latest_news


from telegram_bot import send_message



from news_db import (
    init_db,
    is_published,
    mark_as_published,
)



from category_engine import detect_smart_category



from category_hashtags import get_hashtag



from ai_processor import process_news



from sport_formatter import format_sport_news



from game_formatter import format_game_news



from quality_engine import is_high_quality



from importance_engine import is_important



from formatter import format_news





CHECK_INTERVAL = 300






# =================================
# Sport Categories
# =================================


SPORT_CATEGORIES = {


    "football",
    "basketball",
    "volleyball",
    "tennis",
    "wrestling",
    "formula1",
    "combat",

}








def normalize_category(category):


    if category in SPORT_CATEGORIES:


        return "sport"


    return category











async def check_news():


    news = get_latest_news()



    if not news:


        print(
            "No news found."
        )


        return






    random.shuffle(news)







    for item in news:




        link = item.get(

            "link",

            ""

        )



        if not link:


            link = (

                item.get(
                    "title",
                    ""
                )

                +

                item.get(
                    "source",
                    ""
                )

            )





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



        source = item.get(

            "source",

            ""

        )








        # =========================
        # Category Detection
        # =========================


        detected_category = detect_smart_category(


            title=raw_title,


            summary=raw_summary,


            source=source


        )




        original_category = detected_category




        category = normalize_category(

            detected_category

        )




        print(

            f"📂 Category: {category}"

        )


        print(

            f"🏷️ Original: {original_category}"

        )





        # =========================
        # AI Processing
        # =========================


        processed = process_news(


            raw_title,


            raw_summary


        )



        title = processed.get(

            "title",

            raw_title

        )



        summary = processed.get(

            "summary",

            raw_summary

        )






        sport_data = None

        game_data = None
                  # =========================
        # Sport Processing
        # =========================


        if category == "sport":



            sport_result = format_sport_news(


                title,


                summary


            )




            if sport_result.get("blocked"):


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









        # =========================
        # Gaming Processing
        # =========================


        if category == "gaming":



            game_result = format_game_news(


                title,


                summary

            )



            if game_result.get("blocked"):


                print(

                    "❌ Game video-only skipped"

                )


                continue






            title = game_result.get(

                "title",

                title

            )



            summary = game_result.get(

                "summary",

                summary

            )



            game_data = game_result.get(

                "game"

            )









        # =========================
        # Hashtag Engine
        # =========================


        hashtag_data = get_hashtag(


            category,


            title,


            summary


        )









        # =========================
        # Quality Check
        # =========================


        if not is_high_quality(


            title,


            summary


        ):


            print(

                "❌ Low quality news skipped"

            )


            continue







        # =========================
        # Importance Check
        # =========================


        if not is_important(


            title,


            summary,


            category


        ):


            print(

                "❌ Low importance news skipped"

            )


            continue







        # =========================
        # Telegram Formatter
        # =========================


        message = format_news(


            title=title,


            summary=summary,


            source=source,


            category=category,


            sport=sport_data,


            game=game_data,


            hashtag_data=hashtag_data


        )









        # =========================
        # Telegram Send
        # =========================


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

        "🚀 KhabarF24 Started v7.0"

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

"""
KhabarF24 Game Engine v1.0

وظایف:
- تشخیص خبر گیم
- استخراج نوع بازی
"""


from game_rules import detect_game



def process_game(title, summary=""):


    if not detect_game(title, summary):

        return {

            "is_game": False

        }



    return {

        "is_game": True,

        "type": detect_game_type(
            title,
            summary
        )

    }




def detect_game_type(title, summary):


    text = f"{title} {summary}".lower()



    if "playstation" in text or "ps5" in text:

        return "پلی‌استیشن"



    if "xbox" in text:

        return "ایکس‌باکس"



    if "minecraft" in text:

        return "ماینکرفت"



    if "call of duty" in text or "warzone" in text:

        return "کال آف دیوتی"



    return "گیم"

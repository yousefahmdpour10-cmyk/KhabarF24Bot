from PIL import Image
import requests
import os

# ====================== تنظیمات لوگو ======================
# مسیر لوگو - این مسیر را بعداً درست تنظیم کن
LOGO_PATH = "assets/KhabarF24.png"   # پیشنهاد: داخل پوشه assets

def download_image(image_url: str, save_path="temp_news_image.jpg"):
    """دانلود عکس از منبع"""
    try:
        response = requests.get(image_url, timeout=12)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return save_path
    except Exception as e:
        print(f"خطا در دانلود عکس: {e}")
    return None


def add_khabarf24_watermark(image_path: str, output_path="final_post_image.jpg"):
    """اضافه کردن لوگوی KhabarF24 به صورت کوچک و حرفه‌ای"""
    if not os.path.exists(LOGO_PATH):
        print(f"⚠️ لوگو در مسیر {LOGO_PATH} پیدا نشد!")
        return image_path

    try:
        base = Image.open(image_path).convert("RGBA")
        w, h = base.size

        logo = Image.open(LOGO_PATH).convert("RGBA")
        
        # اندازه مناسب (۱۴ درصد عرض تصویر)
        logo_width = int(w * 0.14)
        logo = logo.resize((logo_width, int(logo_width * logo.height / logo.width)), Image.Resampling.LANCZOS)

        # موقعیت: پایین راست
        padding = 25
        position = (w - logo.width - padding, h - logo.height - padding)

        transparent = Image.new('RGBA', base.size, (0, 0, 0, 0))
        transparent.paste(logo, position, mask=logo)

        final = Image.alpha_composite(base, transparent)
        final.convert("RGB").save(output_path, quality=93)
        
        print("✅ واترمارک با موفقیت اضافه شد")
        return output_path

    except Exception as e:
        print(f"خطا در اضافه کردن لوگو: {e}")
        return image_path

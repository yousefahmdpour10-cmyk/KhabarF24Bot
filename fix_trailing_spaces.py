"""
اسکریپت یک‌بارمصرف: هر پوشه‌ی زیر app/processors که اسمش فاصله‌ی
اضافه‌ی انتهایی دارد را پیدا می‌کند، محتوایش را به پوشه‌ی درست
(بدون فاصله) منتقل می‌کند و پوشه‌ی خراب را پاک می‌کند.

اجرا با:
    python3 fix_trailing_spaces.py

بعد از اجرا و تأیید نتیجه، همین فایل را هم حذف کن.
"""

import os
import shutil

BASE = "app/processors"

for name in os.listdir(BASE):
    stripped = name.rstrip()
    if stripped == name:
        continue  # این پوشه/فایل مشکلی ندارد

    src = os.path.join(BASE, name)
    dst = os.path.join(BASE, stripped)

    if not os.path.isdir(src):
        continue

    print(f"Found broken folder: {name!r} -> merging into {stripped!r}")

    os.makedirs(dst, exist_ok=True)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        print(f"  moving {s!r} -> {d!r}")
        shutil.move(s, d)

    os.rmdir(src)
    print(f"  removed empty folder {name!r}")

print("Done. Current app/processors contents:")
for name in sorted(os.listdir(BASE)):
    print(f"  [{name}]")

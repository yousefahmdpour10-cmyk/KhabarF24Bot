import os
import shutil

BASE = "app/processors"

for name in os.listdir(BASE):
    stripped = name.rstrip()
    if stripped == name:
        continue

    src = os.path.join(BASE, name)
    dst = os.path.join(BASE, stripped)

    if not os.path.isdir(src):
        continue

    print("Found broken folder:", repr(name), "-> merging into", repr(stripped))

    os.makedirs(dst, exist_ok=True)

    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        print("  moving", repr(s), "->", repr(d))
        shutil.move(s, d)

    os.rmdir(src)
    print("  removed empty folder", repr(name))

print("Done. Current app/processors contents:")
for name in sorted(os.listdir(BASE)):
    print("  [" + name + "]")

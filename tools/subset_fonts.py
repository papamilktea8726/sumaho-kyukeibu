"""アプリで使う文字だけを含む軽量フォント (www/fonts) を作る。
web/index.html の文言を変えて新しい漢字を使ったときに実行し直す。
（実行しなくてもアプリは動きます。未収録の文字だけ端末の標準フォントで表示されます）

準備: pip install fonttools brotli
フォント原本: https://github.com/google/fonts の
  ofl/mplusrounded1c/MPLUSRounded1c-{Regular,Medium,Bold,ExtraBold}.ttf
  ofl/delagothicone/DelaGothicOne-Regular.ttf
を tools/fonts-src/ に置く。
使い方: python3 tools/subset_fonts.py
"""
import os
import shutil
from fontTools import subset

SRC = "tools/fonts-src"
OUT = "www/fonts"
FACES = [
    ("Dela Gothic One", 400, "DelaGothicOne-Regular.ttf"),
    ("M PLUS Rounded 1c", 400, "MPLUSRounded1c-Regular.ttf"),
    ("M PLUS Rounded 1c", 500, "MPLUSRounded1c-Medium.ttf"),
    ("M PLUS Rounded 1c", 700, "MPLUSRounded1c-Bold.ttf"),
    ("M PLUS Rounded 1c", 800, "MPLUSRounded1c-ExtraBold.ttf"),
]

text = open("web/index.html", encoding="utf-8").read()
# Android版・iPhone版で追加する文言も含める
for extra in ("tools/build_www.py", "tools/build_pwa.py"):
    text += open(extra, encoding="utf-8").read()
chars = set(text)
for a, b in [(0x20, 0x7E), (0x3000, 0x30FF), (0xFF01, 0xFF5E)]:  # 英数・かな・全角記号
    chars.update(chr(c) for c in range(a, b + 1))
chars = "".join(sorted(c for c in chars if c.isprintable()))

if os.path.isdir(OUT):
    for f in os.listdir(OUT):
        if f.endswith((".woff2", ".css")):
            os.remove(os.path.join(OUT, f))
os.makedirs(OUT, exist_ok=True)

css = []
for family, weight, fname in FACES:
    out_name = fname.replace(".ttf", ".woff2")
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = subset.load_font(os.path.join(SRC, fname), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=chars)
    sub.subset(font)
    subset.save_font(font, os.path.join(OUT, out_name), opts)
    css.append(
        "@font-face{font-family:'%s';font-style:normal;font-weight:%d;font-display:swap;"
        "src:url(%s) format('woff2')}" % (family, weight, out_name)
    )
    print(out_name, os.path.getsize(os.path.join(OUT, out_name)) // 1024, "KB")

open(os.path.join(OUT, "fonts.css"), "w").write("\n".join(css) + "\n")
print(len(chars), "文字を収録")

"""アプリアイコン・通知アイコン・スプラッシュ画像を生成する（豪邸テーマ）。
使い方: python3 tools/make_icons.py  (プロジェクトのルートで実行)
"""
import os
from PIL import Image, ImageDraw

RES = "android/app/src/main/res"
TEAL = (11, 138, 143)
WALL = (255, 248, 236)
WALL2 = (239, 227, 205)
ROOF = (95, 114, 144)
WINDOW = (246, 214, 107)
WATER = (79, 195, 224)
WATER2 = (180, 236, 246)
GOLD = (233, 169, 30)
GOLD2 = (255, 214, 110)
WOOD = (154, 107, 67)
WHITE = (255, 255, 255)


def mansion(d, s, cx, cy, scale, mono=None):
    """豪邸とプール。cy は建物の地面の位置。幅およそ 0.64*k、高さ 0.40k(上) + 0.16k(下)。"""
    k = s * scale
    c = (lambda col: mono) if mono else (lambda col: col)
    X = lambda v: cx + v * k
    Y = lambda v: cy + v * k
    # 両翼
    for sx in (-1, 1):
        x0, x1 = sorted((X(sx * 0.13), X(sx * 0.32)))
        d.polygon([(x0, Y(-0.215)), (x0 + 0.02 * k, Y(-0.26)), (x1 - 0.02 * k, Y(-0.26)), (x1, Y(-0.215))], fill=c(ROOF))
        d.rectangle([x0, Y(-0.215), x1, Y(0)], fill=c(WALL2))
        d.rectangle([x0 - 0.01 * k, Y(-0.225), x1 + 0.01 * k, Y(-0.205)], fill=c(GOLD))
        if not mono:
            for i in range(2):
                wx = x0 + 0.03 * k + i * 0.085 * k
                d.rectangle([wx, Y(-0.17), wx + 0.045 * k, Y(-0.11)], fill=WINDOW)
                d.rectangle([wx, Y(-0.08), wx + 0.045 * k, Y(-0.025)], fill=WINDOW)
    # 中央棟と破風
    d.rectangle([X(-0.13), Y(-0.31), X(0.13), Y(0)], fill=c(WALL))
    d.polygon([(X(-0.15), Y(-0.31)), (X(0), Y(-0.40)), (X(0.15), Y(-0.31))], fill=c(WALL))
    d.rectangle([X(-0.15), Y(-0.325), X(0.15), Y(-0.30)], fill=c(GOLD))
    if not mono:
        d.ellipse([X(-0.022), Y(-0.375), X(0.022), Y(-0.335)], fill=WINDOW)
        # アーチ窓
        d.rectangle([X(-0.05), Y(-0.24), X(0.05), Y(-0.17)], fill=WINDOW)
        d.ellipse([X(-0.05), Y(-0.29), X(0.05), Y(-0.19)], fill=WINDOW)
        d.rectangle([X(-0.13), Y(-0.16), X(0.13), Y(-0.145)], fill=GOLD)
        # 柱
        for px in (-0.115, -0.075, 0.055, 0.095):
            d.rectangle([X(px), Y(-0.145), X(px + 0.022), Y(0)], fill=WALL2)
        # 玄関
        d.rectangle([X(-0.035), Y(-0.07), X(0.035), Y(0)], fill=WOOD)
        d.ellipse([X(-0.035), Y(-0.105), X(0.035), Y(-0.035)], fill=WOOD)
    # プール
    d.rounded_rectangle([X(-0.30), Y(0.035), X(0.30), Y(0.165)], radius=0.045 * k, fill=c(WHITE if not mono else WHITE))
    if mono:
        d.rounded_rectangle([X(-0.27), Y(0.06), X(0.27), Y(0.14)], radius=0.03 * k, fill=(0, 0, 0, 0))
    else:
        d.rounded_rectangle([X(-0.27), Y(0.06), X(0.27), Y(0.14)], radius=0.03 * k, fill=WATER)
        d.line([(X(-0.18), Y(0.095)), (X(-0.08), Y(0.095))], fill=WATER2, width=max(1, int(0.014 * k)))
        d.line([(X(0.04), Y(0.115)), (X(0.16), Y(0.115))], fill=WATER2, width=max(1, int(0.014 * k)))
        # コイン
        cr = 0.07 * k
        ccx, ccy = X(0.30), Y(-0.40)
        d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=GOLD)
        d.ellipse([ccx - cr * .62, ccy - cr * .62, ccx + cr * .62, ccy + cr * .62], outline=GOLD2, width=max(1, int(cr * .18)))


def full_icon(size, round_=False):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if round_:
        d.ellipse([0, 0, s - 1, s - 1], fill=TEAL)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .22), fill=TEAL)
    mansion(d, s, s / 2, s * .64, 1.15)
    return img.resize((size, size), Image.LANCZOS)


def foreground(size):
    # アダプティブアイコン: 108dp中、安全領域は中央66dp
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mansion(d, s, s / 2, s * .58, 0.74)
    return img.resize((size, size), Image.LANCZOS)


def notify(size):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mansion(d, s, s / 2, s * .66, 1.45, mono=WHITE)
    return img.resize((size, size), Image.LANCZOS)


def splash(w, h):
    img = Image.new("RGB", (w, h), TEAL)
    d = ImageDraw.Draw(img)
    s = min(w, h) * 0.55
    mansion(d, s, w / 2, h / 2 + s * .1, 1.0)
    return img


DENS = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
for name, m in DENS.items():
    folder = f"{RES}/mipmap-{name}"
    full_icon(int(48 * m)).save(f"{folder}/ic_launcher.png")
    full_icon(int(48 * m), round_=True).save(f"{folder}/ic_launcher_round.png")
    foreground(int(108 * m)).save(f"{folder}/ic_launcher_foreground.png")
    nd = f"{RES}/drawable-{name}"
    os.makedirs(nd, exist_ok=True)
    notify(int(24 * m)).save(f"{nd}/ic_stat_notify.png")
    pw, ph = int(320 * m), int(480 * m)
    splash(pw, ph).save(f"{RES}/drawable-port-{name}/splash.png")
    splash(ph, pw).save(f"{RES}/drawable-land-{name}/splash.png")
splash(480, 800).save(f"{RES}/drawable/splash.png")
full_icon(512).save("tools/icon-512.png")  # Google Play 掲載用
print("icons done")

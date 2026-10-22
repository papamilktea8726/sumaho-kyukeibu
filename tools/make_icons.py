"""アプリアイコン・通知アイコン・スプラッシュ画像を生成する。
使い方: python3 tools/make_icons.py  (プロジェクトのルートで実行)
"""
import math
import os
from PIL import Image, ImageDraw

RES = "android/app/src/main/res"
TEAL = (11, 138, 143)
SEA = (70, 175, 191)
SAND = (241, 220, 160)
SAND2 = (226, 196, 127)
GRASS = (134, 200, 111)
LEAF = (63, 154, 80)
LEAF2 = (47, 130, 67)
WOOD = (154, 107, 67)
COIN = (233, 169, 30)
WHITE = (255, 255, 255)


def island(d, s, cx, cy, scale):
    """島とヤシの木。scale=1 のとき幅およそ 0.62*s。"""
    k = s * scale
    rx, ry = 0.31 * k, 0.12 * k
    d.ellipse([cx - rx, cy - ry + 0.02 * k, cx + rx, cy + ry + 0.02 * k], fill=SAND2)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=SAND)
    d.ellipse([cx - rx * .8, cy - ry * .85 - 0.015 * k, cx + rx * .8, cy + ry * .5], fill=GRASS)
    # 幹
    tx, ty = cx - 0.02 * k, cy - 0.02 * k
    pts = []
    for i in range(21):
        t = i / 20
        x = tx + math.sin(t * 1.4) * 0.06 * k
        y = ty - t * 0.34 * k
        pts.append((x, y))
    d.line(pts, fill=WOOD, width=max(2, int(0.045 * k)), joint="curve")
    top = pts[-1]
    # 葉
    for ang, col in [(-170, LEAF2), (-130, LEAF), (-50, LEAF), (-10, LEAF2), (-90, LEAF)]:
        r = math.radians(ang)
        for j in range(14):
            t = j / 13
            px = top[0] + math.cos(r) * t * 0.19 * k
            py = top[1] + math.sin(r) * t * 0.19 * k + (t ** 2) * 0.07 * k
            w = 0.035 * k * math.sin(math.pi * min(.95, t + .08))
            d.ellipse([px - w, py - w, px + w, py + w], fill=col)
    # ココナッツ
    for dx in (-0.025, 0.02):
        rr = 0.022 * k
        d.ellipse([top[0] + dx * k - rr, top[1] + 0.03 * k - rr, top[0] + dx * k + rr, top[1] + 0.03 * k + rr], fill=WOOD)
    # コイン
    cr = 0.075 * k
    ccx, ccy = cx + 0.2 * k, cy - 0.27 * k
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=COIN)
    d.ellipse([ccx - cr * .62, ccy - cr * .62, ccx + cr * .62, ccy + cr * .62], outline=(255, 214, 110), width=max(1, int(cr * .18)))


def full_icon(size, round_=False):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if round_:
        d.ellipse([0, 0, s - 1, s - 1], fill=TEAL)
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * .22), fill=TEAL)
    island(d, s, s / 2, s * .66, 1.0)
    return img.resize((size, size), Image.LANCZOS)


def foreground(size):
    # アダプティブアイコン: 108dp中、安全領域は中央66dp
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    island(d, s, s / 2, s * .62, 0.62)
    return img.resize((size, size), Image.LANCZOS)


def notify(size):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 白一色のヤシの木シルエット
    d.ellipse([s * .12, s * .74, s * .88, s * .94], fill=WHITE)
    pts = [(s * .48 + math.sin(t / 20 * 1.4) * s * .1, s * .82 - t / 20 * s * .5) for t in range(21)]
    d.line(pts, fill=WHITE, width=int(s * .09), joint="curve")
    top = pts[-1]
    for ang in (-170, -125, -55, -10):
        r = math.radians(ang)
        for j in range(14):
            t = j / 13
            px = top[0] + math.cos(r) * t * s * .34
            py = top[1] + math.sin(r) * t * s * .3 + t * t * s * .12
            w = s * .065 * math.sin(math.pi * min(.95, t + .08))
            d.ellipse([px - w, py - w, px + w, py + w], fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


def splash(w, h):
    img = Image.new("RGB", (w, h), TEAL)
    d = ImageDraw.Draw(img)
    s = min(w, h) * 0.55
    island(d, s, w / 2, h / 2 + s * .12, 1.0)
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

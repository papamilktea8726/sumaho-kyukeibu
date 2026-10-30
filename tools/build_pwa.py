"""ブラウザ版の index.html を iPhone 向け Webアプリ（GitHub Pages 公開用）に変換する。
使い方: python3 tools/build_pwa.py web/index.html   （プロジェクトのルートで実行）
出力先: site/ （GitHub Actions が GitHub Pages に公開する）
- Google Fonts を同梱フォント (www/fonts) に置き換え（オフラインでも表示が崩れない）
- 「ホーム画面に追加」用のアイコン・manifest・iPhone向けの meta を追加
- Service Worker でオフラインでも起動できるようにする
- iPhone の Safari で開いたときに「ホーム画面に追加」の案内を出す
"""
import hashlib
import json
import os
import re
import shutil
import sys

from PIL import Image

OUT = "site"
TEAL = (11, 138, 143)

src = open(sys.argv[1], encoding="utf-8").read()

# Google Fonts を外し、同梱フォントを使う
src = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n', "", src)
src = re.sub(r'<link rel="preconnect"[^>]*>\n', "", src)
src = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', "", src)

head_part, body_part = src.split('<div class="app">', 1)
body_part = '<div class="app">' + body_part

IOS_JS = r'''
/* ---------- iPhone (Webアプリ版) ---------- */
const IS_IOS=/iP(hone|ad|od)/.test(navigator.userAgent)||(navigator.platform==="MacIntel"&&navigator.maxTouchPoints>1);
const IS_STANDALONE=window.navigator.standalone===true||(window.matchMedia&&matchMedia("(display-mode: standalone)").matches);
if("serviceWorker" in navigator){window.addEventListener("load",()=>{navigator.serviceWorker.register("sw.js").catch(()=>{})})}
function installGuide(){
  openSheet(`<h3>ホーム画面に追加してね</h3>
<p>アプリのように使えて、記録も消えにくくなります。</p>
<ol style="margin:0;padding-left:1.4em;display:grid;gap:6px">
<li>画面の下（または上）にある <b>共有ボタン</b>（□に↑のマーク）をタップ</li>
<li>メニューを下にスクロールして <b>「ホーム画面に追加」</b> をタップ</li>
<li>右上の <b>「追加」</b> をタップ</li>
</ol>
<p class="note">追加したら、ホーム画面の「スマホ休憩部」アイコンから開いてください。Safariで開いた記録とは別になります。</p>
<button class="primary" data-close>わかった</button>`);
}
if(IS_IOS&&!IS_STANDALONE){
  let shown=false;try{shown=sessionStorage.getItem("ios-guide")==="1";sessionStorage.setItem("ios-guide","1")}catch(e){}
  if(!shown)setTimeout(installGuide,700);
}
'''

js = body_part
js = js.replace('const KEY="sumaho-kyukeibu-v1";', 'const KEY="sumaho-kyukeibu-v1";' + IOS_JS, 1)
assert "installGuide" in js, "iPhone用コードの差し込みに失敗"

APP_NAME = "スマホ休憩部"
page = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{APP_NAME}">
<meta name="description" content="スマホを置いた時間がコインになり、家が豪邸へとグレードアップする、中学生向けのスマホ休憩アプリ。">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="stylesheet" href="fonts/fonts.css">
<style>
:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px)}}
body{{margin:0;font:14px system-ui,sans-serif;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
{head_part.strip()}
</head>
<body>
{js}
</body>
</html>
'''

# 出力フォルダを作り直す
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(f"{OUT}/icons")
shutil.copytree("www/fonts", f"{OUT}/fonts")
open(f"{OUT}/index.html", "w", encoding="utf-8").write(page)

# アイコン（iPhoneは透明部分が黒くなるので、角を緑で埋める）
base = Image.open("tools/icon-512.png").convert("RGBA")
full = Image.new("RGBA", base.size, TEAL + (255,))
full.alpha_composite(base)
full = full.convert("RGB")
for name, size in [("apple-touch-icon.png", 180), ("icon-192.png", 192), ("icon-512.png", 512)]:
    full.resize((size, size), Image.LANCZOS).save(f"{OUT}/icons/{name}", optimize=True)

manifest = {
    "name": APP_NAME,
    "short_name": APP_NAME,
    "description": "スマホを置いた時間がコインになる、スマホ休憩アプリ",
    "lang": "ja",
    "start_url": "./",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#E6F4F5",
    "theme_color": "#0B8A8F",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
    ],
}
open(f"{OUT}/manifest.webmanifest", "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2))

# Service Worker（中身が変わるたびにキャッシュ名が変わり、新しい版に入れ替わる）
files = []
for root, _, names in os.walk(OUT):
    for n in sorted(names):
        files.append(os.path.relpath(os.path.join(root, n), OUT).replace(os.sep, "/"))
files.sort()
h = hashlib.sha256()
for f in files:
    h.update(f.encode())
    h.update(open(os.path.join(OUT, f), "rb").read())
version = h.hexdigest()[:10]
assets = ["./"] + [f for f in files if not f.startswith("fonts/LICENSE")]

sw = f'''const CACHE="sumaho-kyukeibu-{version}";
const ASSETS={json.dumps(assets, ensure_ascii=False)};
self.addEventListener("install",e=>{{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()))}});
self.addEventListener("activate",e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))}});
self.addEventListener("fetch",e=>{{
  if(e.request.method!=="GET")return;
  // 画面はネット優先（新しい版をすぐ反映）、つながらなければ保存した版
  if(e.request.mode==="navigate"){{
    e.respondWith(fetch(e.request).then(r=>{{const c=r.clone();caches.open(CACHE).then(x=>x.put("./",c));return r}}).catch(()=>caches.match("./")));
    return;
  }}
  e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));
}});
'''
open(f"{OUT}/sw.js", "w", encoding="utf-8").write(sw)
open(f"{OUT}/.nojekyll", "w").write("")
print(f"{OUT}/ written (version {version}, {len(files)} files)")

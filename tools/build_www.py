"""ブラウザ版の index.html を Android アプリ用 (www/index.html) に変換する。
使い方: python3 tools/build_www.py web/index.html
- Google Fonts を同梱フォント (www/fonts) に置き換え
- ページの <head> を補う
- 休憩終了・起床時刻の通知 (Capacitor LocalNotifications) を追加
"""
import re
import sys

src = open(sys.argv[1], encoding="utf-8").read()

# 不要になる行を除去
src = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n', "", src)
src = re.sub(r'<link rel="preconnect"[^>]*>\n', "", src)
src = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', "", src)

head_part, body_part = src.split('<div class="app">', 1)
body_part = '<div class="app">' + body_part

NATIVE_JS = r'''
/* ---------- Android: 通知 ---------- */
const LN=(window.Capacitor&&window.Capacitor.Plugins&&window.Capacitor.Plugins.LocalNotifications)||null;
const NOTE_ID={focus:1,sleep:2};
async function notifySchedule(a){
  if(!LN)return;
  try{
    let p=await LN.checkPermissions();
    if(p.display!=="granted")p=await LN.requestPermissions();
    if(p.display!=="granted"){toast("通知がオフです。時間がたったらアプリを開いてね");return}
    await LN.cancel({notifications:[{id:1},{id:2}]});
    const sleep=a.type==="sleep";
    await LN.schedule({notifications:[{
      id:sleep?NOTE_ID.sleep:NOTE_ID.focus,
      title:sleep?"おはよう！おやすみチャレンジ成功":"スマホ休憩、達成！",
      body:sleep?"アプリを開いて、ペットの成長を見てみよう。":`${a.min}分おつかれさま。アプリを開いてコインを受け取ろう。`,
      schedule:{at:new Date(a.end),allowWhileIdle:true}
    }]});
  }catch(e){}
}
async function notifyCancel(){if(!LN)return;try{await LN.cancel({notifications:[{id:1},{id:2}]})}catch(e){}}
'''

js = body_part
# 通知関数をスクリプト冒頭に追加
js = js.replace('const KEY="sumaho-kyukeibu-v1";', 'const KEY="sumaho-kyukeibu-v1";' + NATIVE_JS, 1)
# チャレンジ開始時・おやすみ開始時に通知を予約
js = js.replace("save();unlockAudio();showFocus();\n});\n$(\"wakeInput\")",
                "save();unlockAudio();showFocus();notifySchedule(S.active);\n});\n$(\"wakeInput\")", 1)
js = js.replace("save();unlockAudio();showFocus();\n});\n\n/* ---------- focus mode",
                "save();unlockAudio();showFocus();notifySchedule(S.active);\n});\n\n/* ---------- focus mode", 1)
# やめたときは通知を取り消す
js = js.replace('S.active=null;save();clearInterval(tick);$("focus").hidden=true;closeSheet();toast("また挑戦しよう！")',
                'S.active=null;save();clearInterval(tick);notifyCancel();$("focus").hidden=true;closeSheet();toast("また挑戦しよう！")', 1)
# 案内文
js = js.replace("時間がたってから戻ると、コインがもらえます。", "時間になると通知でお知らせします。", 1)
js = js.replace('"スマホを置いて、画面を閉じてOK。時間になったら戻ってきてね。"',
                '"スマホを置いて、画面を閉じてOK。時間になったら通知でお知らせします。"', 1)

assert js.count("notifySchedule(S.active)") == 2, "通知の差し込みに失敗"
assert "notifyCancel();" in js

page = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="stylesheet" href="fonts/fonts.css">
<style>
:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
body{{margin:0;font:14px system-ui,sans-serif;-webkit-user-select:none;user-select:none}}
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
open("www/index.html", "w", encoding="utf-8").write(page)
print("www/index.html written")

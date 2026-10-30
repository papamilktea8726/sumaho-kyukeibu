# スマホ休憩部（Android版・iPhone用Webアプリ版）

中学生向けのスマホ離れアプリです。スマホを置いた時間がコインになり、家が豪邸へとグレードアップします。プール・シャンデリア・スポーツカーなどを買って飾れます。

## スマホに入れる方法

1. GitHubのこのリポジトリを開き、右側の **Releases** から最新の「スマホ休憩部 テスト版」を開く
2. Androidスマホで `sumaho-kyukeibu-v1.0.xx.apk` をタップしてダウンロード
3. 「この提供元のアプリを許可」を求められたらオンにして、インストール
4. 初めてチャレンジを開始したとき「通知を許可」を選ぶ（休憩終了を知らせるため）

新しい版を入れるときは、古い版の上から同じ手順でインストールすれば記録は残ります。

## iPhoneで使う方法（Webアプリ版・無料）

1. iPhoneの **Safari** で https://papamilktea8726.github.io/sumaho-kyukeibu/ を開く
2. 共有ボタン（□に↑のマーク）→「ホーム画面に追加」→「追加」
3. ホーム画面の「スマホ休憩部」アイコンから開く

- 一度開けば、電波がなくても起動できます。
- iPhone版は休憩終了の通知が出ません。時間がたったら自分でアプリを開くと、コインがもらえます。
- 記録はiPhoneの中に保存されます。Safariで開いたときとホーム画面から開いたときでは、記録が別になります。

## 仕組み

| 場所 | 内容 |
|---|---|
| `web/index.html` | アプリ本体（画面・ゲームの仕組み）。直すのは基本ここだけ |
| `tools/build_www.py` | 本体をAndroid用に変換（同梱フォント、通知機能を追加）して `www/` に出力 |
| `tools/build_pwa.py` | 本体をiPhone用Webアプリに変換（アイコン・オフライン対応・ホーム画面追加の案内）して `site/` に出力 |
| `tools/make_icons.py` | アイコン・通知アイコン・起動画面を生成 |
| `android/` | Androidアプリのプロジェクト（Capacitor 8） |
| `.github/workflows/build-apk.yml` | `main` に変更が入るたびに、GitHubが自動でAPKを作りReleasesに公開 |
| `.github/workflows/deploy-web.yml` | `main` に変更が入るたびに、iPhone用WebアプリをGitHub Pagesに公開 |

GitHubの **Actions** タブで「Android APKを作る」→「Run workflow」を押すと、手動でもビルドできます。

## 注意

- 現在の署名鍵（`android/app/test-signing.keystore`）はテスト配布用です。Google Playで公開するときは、本番用の鍵を新しく作り、GitHubの秘密情報（Secrets）に保存して使います。
- データ（コイン・島・記録）はスマホの中だけに保存されます。アプリを削除すると消えます。
- フォント: M PLUS Rounded 1c、Dela Gothic One（SIL Open Font License、`www/fonts/` にライセンス同梱）

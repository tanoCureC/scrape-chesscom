# UNDER CONSTRUCTION

## 何をするものか
chess.comに公開されている情報の内、日章旗属性のプレーヤーについて、下記のデータをスクレイピングします。<br>
* プレーヤー名
* レイティング
* 勝数、負数、引分数
* chess.com登録日
* 最後にログインした日

<br>

レイティングと勝敗数の情報は、Blitz, Bullet, Rapid, 960, Daily 960, Daily の６種類のリーダーボード毎に取得します。<br>
尚、日章旗属性というのは、プレーヤー名についている旗が日章旗という意味です。日本に住んでいる外国人の方、海外に住んでいる日本人の方など様々だと思います。<br>

<br>

## 使用方法
**0run_scripts.py** を実行してください。<br>
リーダーボード毎に6種類の...._leaderboard_dates.csv というファイルが作成されます。これが欲しかったデータです。
このデータを集計したり加工したりしたものが、.ipynbファイルですが、開いてみていただければ分かると思いますので、この説明は割愛させていただきます。<br>

<br>

## 各コードの簡単な説明
0. 0run_scripts.py<br>
下記1.から4.のコードを順番に実行します。<br>
一つのpyファイルにまとめることも可能でしたが、停電など何らかの理由でスクレイピングの中断を余儀なくされた際に、作業途中からの再開を容易にするためにコードを分けました。csvファイルへの出力が頻繁に行われるのも同様の理由です。<br>

1. 1leaderboard.py<br>
日章旗属性の各リーダーボードから、プレーヤー名、レイティング、勝敗情報を取得します。4時間程度かかると思います。<br>

2. 2unique_player_names.py<br>
各リーダーボードでプレーヤーが当然重複しておりますので、重複のないプレーヤーリストを作成します。すぐ終わります。<br>

3. 3unique_player_dates.py<br>
上記2.で作成したリストのプレーヤーのプロフィールページにアクセスし、chess.comへの登録日と最終ログイン日を取得します。最終ログイン日は"3 days ago"のような形で取得しますので、スクレイピングの日時と時差を考慮に入れてchess.comのサーバー時間に計算し直します。ページからページへの遷移に5秒のスリープを設けています。実際にはページの読み込み待機時間もありますので、ページ遷移だけで７秒弱かかります。トータルでものすごく時間がかかります。<br>

4. 4merge_on_player_names.py<br>
上記3.で取得した日付のデータをリーダーボードのデータに合体させます。すぐ終わります。<br>
<br>

## 注意点
* スクレイピングの開始から終了まで多分5-6日ほどかかります。（このreadmeを書いている時点でスクレイピングがまだ終わってませんので概算です）<br>
5日は長すぎるがとりあえず挙動を見てみたいという方は、**1leaderboard.py**でスクレイピングする範囲を狭めてみてください。各リーダーボードの最初の２ページ（各ボード上位100人）のみ等に制限することが可能です。最初の2ページ x 6種類のリーダーボードであれば１時間ほどで終了します。試してみたいという方がいらっしゃいましたら、**1leaderboard.py** の128-130行目をアンコメントして下さい。44-49行目の各リーダーボードのリストを部分的にコメントアウトすることも有効です。<br>
<br>

* Windowsでは動作しません（多分）<br>
これらのコードの作成と実行ははUbuntuベースのDockerコンテナ内で行いました。
私はWindowsでpythonを動かす環境を既に削除しているため確認しておりませんが、**1leaderboard.py** 及び、**3unique_player_dates.py**内の以下のコードを変更すればWindowsで動作すると思います。多分。<br>
  * 23行目 chrome_options .....no-sandbox の行をコメントアウト
  * 30行目 service =...の行をコメントアウト
  * 31行目 driver =...の行をコメントアウト
  * 32行目 # driver =...の行をアンコメント<br>
<br>

* .gitignore に*.csvを含めておりません<br>
成果物がcsvファイルですので、皆様と共有する目的で、敢えて下記のcsvファイルを.gitignoreに含めておりません。その他にも多くのcsvファイルがコードによって生成されますが、それらは.gitignoreに含めております。csvファイルはスクレイピング開始時には不要です。全て削除していただいても.pyコードの実行に影響はありません。残しておいたままでも上書きされますので問題ありません。<br>
  * blitz_leaderboard_dates.csv
  * bullet_leaderboard_dates.csv
  * rapid_leaderboard_dates.csv
  * 960live_leaderboard_dates.csv
  * 960daily_leaderboard_dates.csv
  * daily_leaderboard_dates.csv<br>
<br>

* 最後にログインした日<br>
ニュージーランド時間から逆算してchess.comサーバーのあるサンフランシスコ時間を計算しています。従って、ニュージーランド以外でこのコードを走らせる場合は、若干の誤差が発生します。3unique_player_dates.pyファイルの50-51行目でタイムゾーンを設定しています（ニュージーランドは現在GMT+13時間）。厳密性を求める方はここを自分のタイムゾーンに変更してください。<br>
<br>

* Daily Leaderboard<br>
このリーダーボードはchess.comの問題で壊れていました。非常に多くのページにプレーヤーデータが存在せず、そのため、各ページ下部にある'次ページ'のボタンを押すことでページ遷移することが出来ませんでした。その他のリーダーボードでは'次ページ'ボタンが無効になるまで'次ページボタン'を押すことでページ遷移していますが、Daily Leaderboardに限っては、各ページへのURLを直接指定することでページ遷移し、最終ページ番号（コードを実行する前に目視確認）から１ページ目に到達するまでURLのページ番号を一つずつ減少させていくという方法をとりました。因みに、最終ページ番号は当初7366でしたが、コードで空白ページを開くたびに減少し、今は98になっております。その他のリーダーボードも正しくメンテされていないと思われることが何度かありましたので、その他のボードも最終ページから１ページ目に遡ってスクレイピングするのがいいかもしれません。今回はDailyのリーダーボードのみ最終ページから遡行し、その他のページは１ページ目から'次ページ'のボタンを押すことでページ遷移しています。尚、最終ページから遡行してスクレイピングしたDailyリーダーボードでは、下記未解決問題は発生しませんでした。<br>

<br>

## 未解決問題<br>
1leaderboard.pyでのスクレイピングで、63番目前後のプレーヤーから50人毎に勝敗データのスクレイピングがなぜか上手く行きません。色々調べましたが、原因不明です。全てのリーダーボードで同じ問題が発生します。原因と対処方法がわかる方がいらっしゃいましたら教えていただけると大変うれしいです。尚、最終ページから遡行してスクレイピングしたDailyリーダーボードではこの問題は発生しませんでした。<br>
私の環境のDockerイメージは下記でプルできます。<br>
**docker pull tanocurec/ubun_mini_jupy_scra_multi:latest**<br>
中身はubuntu + miniconda + JupyterLab + Google Chrome、イメージサイズは1.32GB、スクレイピングとデータ可視化用に下記のライブラリを導入済みです。scheduleは今回のスクレイピングでは使用していませんが、同接数の定時スクレイピングのコードで使用しています。numpyは使用しませんが、pandasを導入すると相互依存関係にあるため自動的に導入されるようです。<br>

* selenium
* webdriver_manager
* schedule
* pandas & numpy
* matplotlib
* matplotlib-venn
* seaborn

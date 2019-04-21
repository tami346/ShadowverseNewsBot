# ShadowverseNewsBot

Shadowverseの最新ニュースをマストドンに投稿するBot

## 使い方

1. .env_sampleを .envにリネームして、必要なトークンなどの情報を書き込む
2. cronなどで1時間に1度程度newsbot.pyを実行する
3. Botが動作した日のニュースしか取得しないので注意

## 依存パッケージ

- bottle
- beautifulsoup4
- lxml
- requests
- Mastodon.py
- python-dotenv
- SQLAlchemy
- psycopg2-binary（PostgreSQL使用時）
- mysqlclient（MySQL使用時）

## 更新履歴

- Ver.0.1.5 (2019/04/21)
  - requirements.txtではなくPipfileを使うように変更
- Ver.0.1.4 (2019/03/28)
  - 「現在確認している不具合について」が掲載された日に何度も投稿してしまうバグを修正
- Ver.0.1.3 (2019/03/11)
  - 省略されたタイトルの場合、完全なタイトルを取得するように変更
  - 「現在確認している不具合について」も捕捉するようにした
- Ver.0.1.2 (2019/03/10)
  - Botが動作した日に更新されたニュースのみを取得するように変更
  - 内部処理の変更
- Ver.0.1.1 (2019/03/08)
  - 更新されていないニュースも投稿されてしまうバグを修正
  - 例外処理を形だけ追加
- Ver.0.1.0 (2019/03/07)
  - データベースを使い、更新されたニュースのみをトゥートするようにした
- Ver.0.0.5（2019/02/18）
  - 公式Twitterの転載を考え、過去10件の自分のトゥートをチェックするように変更
- Ver.0.0.4（2019/02/15）
  - 処理の効率化による高速化
- Ver.0.0.3（2019/02/13）
  - 未収載から公開トゥートにした
  - クローリングの間隔を1時間にした
- Ver.0.0.2（2019/02/12）
  - 同じトゥートはしないようにした
- Ver.0.0.1（2019/02/11）
  - 運用開始

## TODO

- まともな例外処理
- 500文字を超えたトゥートをしないように（何もしなくても大丈夫だろう）
- ~~既知の不都合のお知らせをどうするか（URLもタイトルも変更なし）捕捉することにした~~
- ~~更新されたニュースのみをトゥートする~~
- ~~URLが同じニュースで追記したものを捕捉するように~~
- ~~クローリングの間隔を1時間にする~~
- ~~同じトゥートをしないようにする~~

## 参考文献

- [Beautiful Soup でのスクレイピング基礎まとめ 初学者向け](https://qiita.com/liston/items/896c49d46585e32ff7b1)
- [PythonとBeautiful Soupでスクレイピング](https://qiita.com/itkr/items/513318a9b5b92bd56185)
- [herokuで無料のDBを利用する方法](https://vavolab.com/article/2018/05/31/22/16/49/)
- [Python3 の 定番ORM 「 SQLAlchemy 」で MySQL ・ SQLite 等を操作 – 導入からサンプルコード](https://it-engineer-lab.com/archives/1183)
- [Python学習講座 「DB操作」 一覧](https://www.python.ambitious-engineer.com/archives/category/application/db)
- [python-dotenv – .envファイルの値を取得し、ローカルサーバーと本番サーバーで設定します。](https://githubja.com/theskumar/python-dotenv)
- [Python逆引きサンプルコード50選（Mastodon API初級編）](https://takulog.info/exercise-python-for-mastodon-1-answer/)
- [Pythonで始めるHeroku 2018](https://qiita.com/torukashima/items/0d6d00d0186b153d5e45)
- [簡単！Herokuで動くTwitter botをPythonで実装する](https://qiita.com/enomotok_/items/41275dd904c8aa774e72)
- [Pythonのdatetimeで日付や時間と文字列を変換（strftime, strptime）](https://note.nkmk.me/python-datetime-usage/)
- [Pipenvを使ったPython開発まとめ）](https://qiita.com/y-tsutsu/items/54c10e0b2c6b565c887a)
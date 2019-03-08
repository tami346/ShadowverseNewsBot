import os, sys, traceback
from time import sleep
from dotenv import load_dotenv
from mastodon import Mastodon

from urllib import request
from bs4 import BeautifulSoup
import lxml

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 環境変数の読み込み
load_dotenv()

# DB接続

# SQLite 使用時
#engine = create_engine('sqlite:///sample_db.sqlite3')  # スラッシュは3本
# SQLログを表示したい場合には echo=True を指定

# PostgreSQL ドライバにpsycopg2-binaryが使用されます。
engine = create_engine(os.getenv("DATABASE_URL"), encoding="utf-8")
# MySQL ドライバにMySQLdbが使用されます。フォークされたmysqlclientでも問題ありません
#engine = create_engine(os.getenv("DATABASE_URL"), encoding="utf-8")

# Base
Base = declarative_base()


# テーブルクラスを定義
class NewsList(Base):
    """
    NewsListテーブルクラス
    """
    # テーブル名
    __tablename__ = 'newslists'

    # 個々のカラムを定義
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    url = Column(String(50))
    isnew = Column(Boolean, default=False)


def scraping():
    '''
        クローリング＆スクレイピングして更新されたニュースをDBに格納する
    '''
    try:
        #クローリングしたいURLを指定
        html = request.urlopen("https://shadowverse.jp/news/")

        #BueatifulSoupのパーサーにはlxmlを使用する
        soup = BeautifulSoup(html, "lxml")

        # ニュースタイトルへのリンクをすべて取得
        sv_newslinks = soup.find_all("a", attrs={"class": "title-link"})

        # テーブルクラスのテーブルを生成
        Base.metadata.create_all(engine)

        # セッション生成
        Session = sessionmaker(bind=engine)
        session = Session()

        # データベースからデータを読み出す
        saved_datas = session.query(NewsList).all()

        # 比較する新着ニュースの数
        news_count = 5

        for sv_newslink in sv_newslinks:
            # 5つのニュースを取得。それ以上は無視する
            if news_count > 0:
                # ニュースのタイトルを取得
                news_title = sv_newslink.find("h4").string

                # ニュースのURLを取得
                news_link = sv_newslink.get("href")

                # 新着ニュースか否か
                new_news = True

                # データベースの情報と比較
                for saved_data in saved_datas:
                    # データベースにすでに存在している記事か確認
                    if saved_data.url == news_link:
                        # タイトルとURLが両方とも同じの場合は既存の記事だからスルー
                        if saved_data.title == news_title:
                            new_news = False
                            break
                        # 追記の場合はURLは変わらずタイトルが変わる
                        else:
                            new_news = False
                            # 追記のタイトルに変更してDBを更新
                            saved_data.title = news_title
                            saved_data.isnew = True
                            session.commit()
                            break


                # 既存の記事と一致しない場合
                if new_news:
                    # 新規ニュースとしてデータベースに登録
                    session.add(NewsList(
                        title=news_title,
                        url=news_link,
                        isnew=True)
                    )

                # 比較した記事数を1つ増やす
                news_count -= 1
            # 5つの記事を比較したらループを抜ける
            else:
                break

        # コミット（データ追加を実行）
        session.commit()

    except:
        sys.stderr.write(traceback.format_exc())

    finally:
        session.close()


def bottoot():
    '''
        更新されたニュースをトゥートする
    '''
    try:
        # アクセスするインスタンスとアカウントを指定
        mastodon = Mastodon(
            access_token = os.getenv("ACCESS_TOKEN"),
            client_id = os.getenv("CLIENT_ID"),
            client_secret = os.getenv("CLIENT_SECRET"),
            api_base_url = os.getenv("MSTDN_URL")
        )

        # セッション生成
        Session = sessionmaker(bind=engine)
        session = Session()

        # NewsListテーブルの投稿されていないものをトゥートする
        newslists = session.query(NewsList).filter_by(isnew=True).all()
        for newslist in newslists:
            # トゥートする
            mastodon.status_post(
# 未収載           visibility = 'unlisted',
# 非公開           visibility='private',
# 隠すテキスト     spoiler_text = '最新のニュース',
                status = newslist.title + "\n" \
                    + "https://shadowverse.jp" + newslist.url + "\n\n" \
                    + '#OfficialNews'
            )
            # 投稿したのでチェックを外す
            newslist.isnew = False
            # それを反映させる
            session.add(newslist)
            # 連続投稿にならないように１秒休ませる
            sleep(1)

        # コミット（データ追加を実行）
        session.commit()

    except:
        sys.stderr.write(traceback.format_exc())

    finally:
        session.close()

# Mastodon.pyの使い方
# https://qiita.com/itsumonotakumi/items/1f9273a07f1f7189921f


# 今は関数を呼び出すだけ
if __name__ == "__main__":
    scraping()
    bottoot()

import os, sys, traceback
from datetime import datetime, timedelta
from time import sleep
from dotenv import load_dotenv
from mastodon import Mastodon

from urllib import request
from bs4 import BeautifulSoup
import lxml

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
#engine = create_engine(os.getenv("DATABASE_URL")+"?charset=utf8", encoding="utf-8")

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
    created_at = Column(DateTime, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))



def scraping():
    '''
        クローリング＆スクレイピングして更新されたニュースをDBに格納する
    '''
    try:
        #クローリングしたいURLを指定
        html = request.urlopen("https://shadowverse.jp/news/")
        #BueatifulSoupのパーサーにはlxmlを使用する
        soup = BeautifulSoup(html, "lxml")
        # ニュースタイトルが入っているブロックを10件取得
        sv_news_blocks = soup.find_all("div", attrs={"class", "list-wrap"}, limit=10)

        # 現在日時の取得
        now_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # サイトの日付の書式
        news_today = datetime.now().strftime("%Y.%m.%d")
        # 30日前の日時
        ago_30days = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

        # テーブルクラスのテーブルを生成
        Base.metadata.create_all(engine)
        # データベースのセッション生成
        Session = sessionmaker(bind=engine)
        session = Session()
        # データベースから30日前までのデータを降順で読み出す
        saved_datas = session.query(NewsList). \
            filter(NewsList.created_at > ago_30days). \
            order_by(NewsList.created_at.desc()). \
            all()

        # reversed(sv_news_blocks) で逆から要素を取り出す
        for sv_news_block in reversed(sv_news_blocks):
            # timeタグが今日なら
            if sv_news_block.time.string == news_today:
                # ニュースタイトルへのリンクをすべて取得
                sv_newslink = sv_news_block.find("a", attrs={"class": "title-link"})
                # ニュースのURLを取得
                news_link = sv_newslink.get("href")
                # ニュースのタイトルを取得
                news_title = sv_newslink.find("h4").string
                # タイトルの末尾が...の場合
                if "..." in news_title:
                    pageurl = request.urlopen("https://shadowverse.jp" + news_link)
                    page = BeautifulSoup(pageurl, "lxml")
                    # 個別ページに行ってニュースタイトルを取得
                    news_title = page.find("h3").string

                # 新着ニュースか否か
                new_news = True
                # データベースの情報と比較
                for saved_data in saved_datas:
                    # データベースにすでに存在している記事か確認
                    if saved_data.url == news_link:
                        # タイトルとURLが両方とも同じの場合は既存の記事だからスルー
                        if saved_data.title == news_title:
                            new_news = False
                            # 現在確認している不具合について
                            if "現在確認している不具合について" == news_title:
                                # 更新日時を変更してDBを更新
                                saved_data.isnew = True
                                saved_data.created_at = now_date_time
                                session.commit()
                                break
                            else:
                                break
                        # 追記の場合はURLは変わらずタイトルが変わる
                        else:
                            new_news = False
                            # 追記のタイトルに変更してDBを更新
                            saved_data.title = news_title
                            saved_data.isnew = True
                            saved_data.created_at = now_date_time
                            session.commit()
                            break

                # 既存の記事と一致しない場合
                if new_news:
                    # 新規ニュースとしてデータベースに登録
                    session.add(NewsList(
                        title=news_title,
                        url=news_link,
                        isnew=True,
                        created_at=now_date_time)
                    )

        # コミット（データ追加を実行）
        session.commit()

    except:
        # エラー内容の出力
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

        # データベースのセッション生成
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
        # エラー内容の出力
        sys.stderr.write(traceback.format_exc())

    finally:
        session.close()

# Mastodon.pyの使い方
# https://qiita.com/itsumonotakumi/items/1f9273a07f1f7189921f


# 今は関数を呼び出すだけ
if __name__ == "__main__":
    scraping()
    bottoot()

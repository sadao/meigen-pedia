# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from django.utils import feedgenerator
from google.appengine.ext import webapp
from models import Meigen
from viewer import Viewer

TEMPLATE_PATH = 'templates/portal/index.html'
class RssHandler(webapp.RequestHandler):
  def get(self):
    # 新着名言を指定数取得する
    query = Meigen.all().order('-created_on')
    meigens = query.fetch(limit = 1000)

    # フィード作成
    feed = feedgenerator.Rss201rev2Feed(
      title = "名言ペディアRSS",
      link = "http://meigen-pedia.appspot.com/rss",
      description = "名言ペディアの全名言です",
      language = u"ja")

    for meigen in meigens:
      # フィードにエントリを追加
      feed.add_item(
        title = meigen.text,
        link = "http://meigen-pedia.appspot.com/word/" + str(meigen.key()),
        description = "by " + meigen.person.name )

    # RSS 文字列にする
    rss = feed.writeString("utf-8")

    # 画面を表示する
    self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    self.response.out.write( rss )

# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.ext import webapp
from models import Meigen
from viewer import Viewer

TEMPLATE_PATH = 'templates/portal/index.html'
DISPLAY_NUMBER = 6
class PortalIndexHandler(webapp.RequestHandler):
  def get(self):
    # 新着名言を指定数取得する
    query = Meigen.all().order('-created_on')
    meigens = query.fetch( limit = DISPLAY_NUMBER )

    # 画面を表示する
    # http://morchin.sakura.ne.jp/effective_python/method.html
    Viewer.generate(Viewer(), self.response, TEMPLATE_PATH, { 'meigens': meigens })


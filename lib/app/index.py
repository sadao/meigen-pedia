# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.api import users
from google.appengine.ext import webapp
from models import Meigen
from viewer import Viewer

TEMPLATE_PATH = 'templates/app/index.html'
DISPLAY_NUMBER = 10
class AppIndexHandler(webapp.RequestHandler):
  def get(self):
    # 所有する新着名言を指定数取得する
    query = Meigen.all()
    query.filter( 'owner = ', users.get_current_user() )
    query.order('-created_on')
    owned_meigens = query.fetch( limit = DISPLAY_NUMBER )

    # 画面を表示する
    Viewer.generate(Viewer(), self.response, TEMPLATE_PATH, { 'meigens': owned_meigens } )

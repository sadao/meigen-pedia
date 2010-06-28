# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.api import users
from google.appengine.ext import webapp
from models import Account
from viewer import Viewer

TEMPLATE_PATH = 'templates/app/settings.html'
class AppSettingsHandler(webapp.RequestHandler):
  def get(self):
    # Userモデルに未登録だったら登録する
    user_obj = users.get_current_user()
    account = Account.get_or_insert(
                   user_obj.user_id(),
                   owner = user_obj,
                   user_id = user_obj.user_id() )

    # 画面表示
    Viewer.generate(Viewer(), self.response, TEMPLATE_PATH, {} )


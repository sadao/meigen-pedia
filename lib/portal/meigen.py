# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.ext import webapp
from models import Meigen,Person
from viewer import Viewer

LIST_TEMPLATE_PATH = 'templates/portal/meigen.html'
INDIVIDUA_TEMPLATE_PATH = 'templates/portal/meigen_individual.html'
# ポータルページの名言ページを表示します
class PortalMeigenHandler(webapp.RequestHandler):
  def get(self, meigen_id):
    # 名言個別ページを表示する
    if meigen_id:
      PortalMeigenHandler.individual(self, meigen_id)
    # 名言一覧ページを表示する
    else:
      Viewer.generate(Viewer(), self.response, LIST_TEMPLATE_PATH, { 'meigens': Meigen.all().order('-created_on') })

  # 名言個別ページ
  def individual(self, meigen_id):
    meigen_obj = Meigen.get(meigen_id)
    message = ''
    if (not meigen_obj):
      message = '指定された名言は登録されていません'

    # 発言者の名言を取得
    query = Meigen.all().order('-created_on')
    query.filter( 'person = ', meigen_obj.person )
    meigens_of_person = query.fetch( limit = 6 )

    Viewer.generate(Viewer(), self.response, INDIVIDUA_TEMPLATE_PATH, 
    {
      'current_meigen': meigen_obj,
      'meigens_of_person': meigens_of_person,
      'meigens': Meigen.all().order('-created_on'),
      'message': message })


# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.ext import webapp
from models import Meigen,Person
from viewer import Viewer

LIST_TEMPLATE_PATH = 'templates/portal/person.html'
INDIVIDUAL_TEMPLATE_PATH = 'templates/portal/person_individual.html'
class PortalPersonHandler(webapp.RequestHandler):
  # ポータルページ：発言者一覧ページを表示する
  def get(self, person_id):
    # 発言者個別ページを表示する
    if person_id:
      PortalPersonHandler.individual(self, person_id)
    else:
      Viewer.generate(Viewer(), self.response, LIST_TEMPLATE_PATH, {'persons': Person.all().order('-created_on') })

  # ポータルページ：発言者個別ページを表示する
  def individual(self, person_id):
    # 発言者取得
    person_obj = Person.get(person_id)
    message = ''
    if (not person_obj):
      message = '指定された発言者は登録されていません'

    # 発言者の名言を取得
    query = Meigen.all().order('-created_on')
    query.filter( 'person = ', person_obj )
    meigens_of_person = query.fetch( limit = 1000 )

    Viewer.generate(Viewer(), self.response, INDIVIDUAL_TEMPLATE_PATH, 
    { 'current_person': person_obj,
      'current_meigens': meigens_of_person,
      'persons': Person.all().order('-created_on'),
      'message': message })


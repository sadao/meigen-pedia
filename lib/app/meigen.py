# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.api import users
from google.appengine.ext import webapp
from models import Meigen,Person
from viewer import Viewer
import urls

TEMPLATE_PATH = 'templates/app/word.html'
DEFAULT_TWITTER_ID = 'TwitterID'
class AppMeigenHandler(webapp.RequestHandler):
  # 名言一覧ページ表示
  def get(self):
    # 所有する発言者のみ取得する
    query = Person.all()
    query.filter( 'owner = ', users.get_current_user() )
    query.order('-created_on')
    owned_persons = query.fetch(limit = 1000)

    # 所有する名言のみ取得する
    query = Meigen.all()
    query.filter( 'owner = ', users.get_current_user() )
    query.order('-created_on')
    owned_meigens = query.fetch(limit = 1000)

    # 編集確認
    meigen_id = self.request.get("id")
    meigen_obj = ''
    if (meigen_id):
      meigen_obj = Meigen.get( meigen_id )

    # 画面を表示する
    Viewer.generate(Viewer(), self.response, TEMPLATE_PATH, 
      {'persons': owned_persons,
       'meigens': owned_meigens,
       'current_meigen': meigen_obj })

  # 名言登録 & 更新
  def post(self):
    mode = self.request.get("mode")
    # 削除処理へ
    if (mode == 'delete'):
      AppMeigenHandler.delete(self)
    # 登録／更新処理へ
    else:
      AppMeigenHandler.insert_or_update(self)

  # 名言削除
  def delete(self):
    # 必須パラメータ取得
    meigen_id = self.request.get("id")
    if (not meigen_id):
      self.redirect(urls.APP_MEIGEN_URL)
      return

    # Person取得
    meigen_obj = Meigen.get( meigen_id )
    if (not meigen_obj):
      self.redirect(urls.APP_MEIGEN_URL)
      return

    # Person 削除
    meigen_obj.delete()

    # 発言者一覧へリダイレクト
    self.redirect(urls.APP_MEIGEN_URL)

  def insert_or_update(self):
    # パラメータ取得
    person_name = self.request.get("person")
    text = self.request.get("text")
    is_lock = self.request.get("is_lock")

    # パラメタが不正なときは一覧画面へリダイレクトする
    if (person_name == '' or text == '' or is_lock == ''):
      self.redirect(urls.APP_MEIGEN_URL)
      return

    # is_lock 補正
    if (is_lock == 'True'):
      is_lock = True
    else:
      is_lock = False
    
    # 発言者登録
    person_obj = Person.get_or_insert(
                   person_name,
                   owner = users.get_current_user(),
                   name = person_name,
                   description = '',
                   twitter_id = DEFAULT_TWITTER_ID,
                   is_lock = is_lock )

    # 名言文(Meigen.text)が変更されたら、変更前のオブジェクトは削除する
    if self.request.get("id"):
      meigen_obj = Meigen.get( self.request.get("id") )
      if meigen_obj and meigen_obj.text != text:
        meigen_obj.delete()

    # 名言登録
    meigen_obj = Meigen.get_or_insert( 
                   text,
                   owner = users.get_current_user(),
                   text = text,
                   person = person_obj,
                   is_lock = is_lock )
    meigen_obj.person = person_obj
    meigen_obj.save()

    # 一覧ページへリダイレクトする
    self.redirect( urls.APP_MEIGEN_URL )


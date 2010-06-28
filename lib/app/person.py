# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

from google.appengine.api import users
from google.appengine.ext import webapp
from models import Meigen,Person
from viewer import Viewer

TEMPLATE_PATH = 'templates/app/person.html'
DEFAULT_TWITTER_ID = 'TwitterID'
class AppPersonHandler(webapp.RequestHandler):
  # 発言者一覧ページ表示
  def get(self):
    # 編集確認
    person_id = self.request.get("id")
    person_obj = ''
    if (person_id):
      person_obj = Person.get( person_id )

    # 所有しない発言者IDを指定された場合は一覧へリダイレクトする
    if person_obj and person_obj.owner != users.get_current_user():
      self.redirect(urls.APP_PERSON_URL)
      return

    # 所有する発言者を取得します
    query = Person.all()
    query.filter( 'owner = ', users.get_current_user() )
    query.order('-created_on')
    owned_persons = query.fetch(limit = 1000)

    # 所有する発言者の名言を取得する
    meigens = ''
    if person_obj:
      query = Meigen.all()
      query.filter( 'owner = ', users.get_current_user() )
      query.filter( 'person = ', person_obj )
      meigens = query.fetch(limit = 1000)

    # 画面を表示する
    Viewer.generate(Viewer(), self.response, TEMPLATE_PATH, { 'persons': owned_persons, 'current_person': person_obj, 'meigens': meigens } )

  # 発言者変更処理
  def post(self):
    mode = self.request.get("mode")
    # 削除処理へ
    if (mode == 'delete'):
      AppPersonHandler.delete(self)
    # 登録／更新処理へ
    else:
      AppPersonHandler.insert_or_update(self)

  # Insert or Update
  def insert_or_update(self):
    # パラメータ取得
    person_name = self.request.get("name")
    person_description = self.request.get("description")
    is_lock = self.request.get("is_lock")

    # パラメタが不正なときは一覧画面へリダイレクトする
    if (person_name == '' or is_lock == ''):
      self.redirect(urls.APP_PERSON_URL)
      return

    # is_lock を Boolean型にする
    if (is_lock == 'True'):
      is_lock = True
    else:
      is_lock = False

    # TwitterID
    twitter_id = self.request.get("twitter_id")

    # 更新
    if self.request.get("id"):
      # Person取得
      person_obj = Person.get( self.request.get("id") )
      if (not person_obj):
        self.redirect(urls.APP_PERSON_URL)

      # Personの所有する名言を取得
      query = Meigen.all()
      query.filter( 'person = ', person_obj )
      owned_meigens = query.fetch(limit = 1)

      # 名言が１つ以上所属している場合は発言者名を変更できない！！とエラーであることを知らせる
      if person_obj.name != person_name and owned_meigens:
        self.redirect(urls.APP_PERSON_URL)
      # Person 削除
      else:
      	person_obj.delete()

    # Person 登録
    person_obj = Person.get_or_insert(
                   person_name,
                   owner = users.get_current_user(),
                   name = person_name,
                   description = person_description,
                   twitter_id = twitter_id,
                   is_lock = is_lock )

    # 発言者一覧へリダイレクト
    self.redirect(urls.APP_PERSON_URL)

  # Person削除
  def delete(self):
    # 必須パラメータ取得
    person_id = self.request.get("id")
    if (not person_id):
      self.redirect(urls.APP_PERSON_URL)

    # Person取得
    person_obj = Person.get( person_id )
    if (not person_obj):
      self.redirect(urls.APP_PERSON_URL)

    # Personが所有する名言を取得する
    query = Meigen.all()
    query.filter( 'person = ', person_obj )
    meigens = query.fetch(limit = 1)

    if (meigens):
      # 名言が１つ以上あるから削除できません。メッセージを出す
      self.redirect(urls.APP_PERSON_URL)
      return

    # Person 削除
    person_obj.delete()

    # 発言者一覧へリダイレクト
    self.redirect(urls.APP_PERSON_URL)


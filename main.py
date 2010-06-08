# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './')

import re
import logging
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from email.header import decode_header
import datetime
import hashlib
import os
import random
import custom_filter
from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# Django template custom_filter library
webapp.template.register_template_library('custom_filter')

## モデル
# Googleアカウントモデル
class Account(db.Model):
  user_id = db.StringProperty(required=True)
  owner = db.UserProperty(required=True)

# 発言者モデル
class Person(db.Model):
  owner = db.UserProperty(required=True)
  name = db.StringProperty(required=True)
  description = db.StringProperty()
  is_lock = db.BooleanProperty()
  twitter_id = db.StringProperty()
  created_on = db.DateTimeProperty(auto_now_add=True)
  modified_on = db.DateTimeProperty(auto_now_add=True)

# 名言モデル
class Meigen(db.Model):
  owner = db.UserProperty(required=True)
  text = db.StringProperty(required=True)
  person = db.ReferenceProperty(Person)
  is_lock = db.BooleanProperty()
  created_on = db.DateTimeProperty(auto_now_add=True)
  modified_on = db.DateTimeProperty(auto_now_add=True)

# メール送信宛先モデル
class Mail(db.Model):
  mailaddress = db.StringProperty(required=True)
  nickname = db.StringProperty()
  date_on = db.DateTimeProperty(auto_now_add=True)

#CONTENT_TYPE = 'text/html; charset=utf-8'
# 画面を生成する
CONTENT_TYPE = 'text/html; charset=utf-8'
def generate_display(self, template_path, template_parameter):
  path = os.path.join( os.path.dirname(__file__), template_path )

  # ログイン済み情報を設定する
  if users.get_current_user():
    template_parameter['user_id'] = users.get_current_user().user_id()
    template_parameter['nickname'] = users.get_current_user().nickname()
    template_parameter['logout_url'] = users.create_logout_url(APP_MEIGEN_URL)

  self.response.headers['Content-Type'] = CONTENT_TYPE
  self.response.out.write( template.render(path, template_parameter) )

# URL定義
PORTAL_INDEX_URL = '/'
PORTAL_MEIGEN_URL = '/word/(.*)'
PORTAL_PERSON_URL = '/person/(.*)'
APP_INDEX_URL = '/app/'
APP_MEIGEN_URL = '/app/word/'
APP_PERSON_URL = '/app/person/'
APP_SETTINGS_URL = '/app/settings/'

# テンプレートパス定義
PORTAL_INDEX_HTML = 'templates/portal/index.html'
PORTAL_MEIGEN_HTML = 'templates/portal/meigen.html'
PORTAL_MEIGEN_INDIVIDUAL_HTML = 'templates/portal/meigen_individual.html'
PORTAL_PERSON_HTML = 'templates/portal/person.html'
PORTAL_PERSON_INDIVIDUAL_HTML = 'templates/portal/person_individual.html'
RESULT_HTML = 'templates/app/result.html'
PROFILE_HTML = 'templates/app/profile.html'
AUTHOR_HTML = 'templates/app/author.html'
APP_INDEX_HTML = 'templates/app/index.html'
APP_MEIGEN_HTML = 'templates/app/word.html'
APP_PERSON_HTML = 'templates/app/person.html'
APP_SETTINGS_HTML = 'templates/app/settings.html'

## ポータル
# ポータルページのTopを表示します
PORTAL_INDEX_DISPLAY_NUMBER = 6
class PortalIndexHandler(webapp.RequestHandler):
  def get(self):
    # 新着名言を指定数取得する
    query = Meigen.all().order('-created_on')
    meigens = query.fetch( limit = PORTAL_INDEX_DISPLAY_NUMBER )

    # 画面を表示する
    generate_display(self, PORTAL_INDEX_HTML, { 'meigens': meigens })

# ポータルページの名言ページを表示します
class PortalMeigenHandler(webapp.RequestHandler):
  def get(self, meigen_id):
    # 名言個別ページを表示する
    if meigen_id:
      PortalMeigenHandler.individual(self, meigen_id)
    # 名言一覧ページを表示する
    else:
      generate_display(self, PORTAL_MEIGEN_HTML, { 'meigens': Meigen.all().order('-created_on') })

  # 名言個別ページ
  def individual(self, meigen_id):
    meigen_obj = Meigen.get(meigen_id)
    message = ''
    if (not meigen_obj):
      message = '指定された名言は登録されていません'

    generate_display(self, PORTAL_MEIGEN_INDIVIDUAL_HTML, 
    {
      'current_meigen': meigen_obj,
      'meigens': Meigen.all().order('-created_on'),
      'message': message })

# ポータルページの発言者ページを表示します
class PortalPersonHandler(webapp.RequestHandler):
  def get(self, person_id):
    # 発言者個別ページを表示する
    if person_id:
      PortalPersonHandler.individual(self, person_id)
    else:
      generate_display(self, PORTAL_PERSON_HTML, {'persons': Person.all().order('-created_on') })

  # 発言者個別ページ
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

    generate_display(self, PORTAL_PERSON_INDIVIDUAL_HTML, 
    { 'current_person': person_obj,
      'current_meigens': meigens_of_person,
      'persons': Person.all().order('-created_on'),
      'message': message })

## App
# 管理画面：インデックスページ
APP_INDEX_DISPLAY_NUMBER = 10
class AppIndexHandler(webapp.RequestHandler):
  def get(self):
    # 所有する新着名言を指定数取得する
    query = Meigen.all()
    query.filter( 'owner = ', users.get_current_user() )
    query.order('-created_on')
    owned_meigens = query.fetch( limit = APP_INDEX_DISPLAY_NUMBER )

    # 画面を表示する
    generate_display( self, APP_INDEX_HTML, { 'meigens': owned_meigens } )

# 管理画面：名言一覧ページ
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
    generate_display( self, APP_MEIGEN_HTML, 
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
      self.redirect(APP_MEIGEN_URL)
      return

    # Person取得
    meigen_obj = Meigen.get( meigen_id )
    if (not meigen_obj):
      self.redirect(APP_MEIGEN_URL)
      return

    # Person 削除
    meigen_obj.delete()

    # 発言者一覧へリダイレクト
    self.redirect(APP_MEIGEN_URL)

  def insert_or_update(self):
    # パラメータ取得
    person_name = self.request.get("person")
    text = self.request.get("text")
    is_lock = self.request.get("is_lock")

    # パラメタが不正なときは一覧画面へリダイレクトする
    if (person_name == '' or text == '' or is_lock == ''):
      self.redirect(APP_MEIGEN_URL)
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
    self.redirect( APP_MEIGEN_URL )

# 管理画面：発言者編集
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
      self.redirect(APP_PERSON_URL)
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
    generate_display( self, APP_PERSON_HTML, { 'persons': owned_persons, 'current_person': person_obj, 'meigens': meigens } )

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
      self.redirect(APP_PERSON_URL)
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
        self.redirect(APP_PERSON_URL)

      # Personの所有する名言を取得
      query = Meigen.all()
      query.filter( 'person = ', person_obj )
      owned_meigens = query.fetch(limit = 1)

      # 名言が１つ以上所属している場合は発言者名を変更できない！！とエラーであることを知らせる
      if person_obj.name != person_name and owned_meigens:
        self.redirect(APP_PERSON_URL)
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
    self.redirect(APP_PERSON_URL)

  # Person削除
  def delete(self):
    # 必須パラメータ取得
    person_id = self.request.get("id")
    if (not person_id):
      self.redirect(APP_PERSON_URL)

    # Person取得
    person_obj = Person.get( person_id )
    if (not person_obj):
      self.redirect(APP_PERSON_URL)

    # Personが所有する名言を取得する
    query = Meigen.all()
    query.filter( 'person = ', person_obj )
    meigens = query.fetch(limit = 1)

    if (meigens):
      # 名言が１つ以上あるから削除できません。メッセージを出す
      self.redirect(APP_PERSON_URL)
      return

    # Person 削除
    person_obj.delete()

    # 発言者一覧へリダイレクト
    self.redirect(APP_PERSON_URL)

# 管理画面：設定
class AppSettingsHandler(webapp.RequestHandler):
  def get(self):
    # Userモデルに未登録だったら登録する
    user_obj = users.get_current_user()
    account = Account.get_or_insert(
                   user_obj.user_id(),
                   owner = user_obj,
                   user_id = user_obj.user_id() )

    # 画面表示
    generate_display( self, APP_SETTINGS_HTML, {} )

# メール受信
# http://appengine-cookbook.appspot.com/recipe/receive-mail/
# https://code.google.com/intl/ja/appengine/docs/python/mail/receivingmail.html
class MailHandler(InboundMailHandler):
  def receive(self, message):
    # User 登録済み確認
    user_id = self.get_user_id( message.to )
    query = Account.all()
    query.filter( 'user_id = ', user_id )
    account = query.fetch( limit = 1 )

    if not account:
      logging.error( 'Account not found. ' + user_id )
      return

    # Subject(= Person) and Body(= Meigen)
    subject = self.get_subject( message.subject )
    body = self.get_body( message )
    if not subject or not body:
      logging.error( 'Subject or Body is non. ' )
      return

    # Person(= Subject) を get_or_insert
    default_is_lock = False
    person_obj = Person.get_or_insert(
                   subject,
                   owner = account[0].owner,
                   name = subject,
                   description = '',
                   twitter_id = '',
                   is_lock = default_is_lock )

    # Meigen(= body) を get_or_insert
    meigen_obj = Meigen.get_or_insert( 
                   body,
                   owner = account[0].owner,
                   text = body,
                   person = person_obj,
                   is_lock = default_is_lock )

    logging.info( 'push mail - ' + message.sender )
    logging.info( 'owner is ' + account[0].owner.email() )

  # あて先メールアドレスの @ の左辺を取得する
  # http://www40.atwiki.jp/geiinbashoku/pages/23.html#id_93404844
  def get_user_id(self, to_address):
    m = re.search(r"(\w+)@(\w+)", to_address)
    return m.group(1)

  # Subject をデコードする
  def get_subject(self, subject):
    encodedsubject = decode_header(subject)
    subj = encodedsubject[0][0]
    encoding = encodedsubject[0][1]
    if encoding:
      subj = subj.decode(encoding)
    if not isinstance(subj, unicode):
      subj = unicode(subj)

    return subj

  def get_body(self, message):
    bodies = message.bodies(content_type='text/plain')
    first_line_of_bodies = "";
    for body in bodies:
      first_line_of_bodies = body[1].decode()
      first_line_of_bodies = first_line_of_bodies.rstrip()
      break

    return first_line_of_bodies

# webapp フレームワークのURLマッピングです
application = webapp.WSGIApplication([
                (PORTAL_INDEX_URL, PortalIndexHandler),
                (PORTAL_MEIGEN_URL, PortalMeigenHandler),
                (PORTAL_PERSON_URL, PortalPersonHandler),
                (APP_INDEX_URL, AppIndexHandler),
                (APP_MEIGEN_URL, AppMeigenHandler),
                (APP_PERSON_URL, AppPersonHandler),
                (APP_SETTINGS_URL, AppSettingsHandler),
                MailHandler.mapping(),
              ], debug=True)

# WebApp フレームワークのメインメソッドです
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

import os
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from models import Person

CONTENT_TYPE = 'text/html; charset=utf-8'
class SearchPersonHandler(webapp.RequestHandler):
  # サジェストで使う
  # 発言者一覧を返却する
  def get(self):
    self.response.headers['Content-Type'] = CONTENT_TYPE

    # Googleアカウントにログインしていなければ何も返さない
    if not users.get_current_user():
      self.response.out.write('')
      return

    # 検索文字列が空の場合、何も返さない
    query = self.request.get('q')
    if not query:
      self.response.out.write('')
      return

    # 検索文字列に前方一致する発言者名一覧を取得する
    owned_persons_upper = db.GqlQuery('SELECT * FROM Person WHERE owner = :1 AND name >= :2 AND name < :3', users.get_current_user(), query.upper(), query.upper() + u'\uFFFD')
    owned_persons_lower = db.GqlQuery('SELECT * FROM Person WHERE owner = :1 AND name >= :2 AND name < :3', users.get_current_user(), query.lower(), query.lower() + u'\uFFFD')

    # 結果を出力する
    for person in (owned_persons_upper):
      self.response.out.write( person.name + "\n" )

    for person in (owned_persons_lower):
      self.response.out.write( person.name + "\n" )


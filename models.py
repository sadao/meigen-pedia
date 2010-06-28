# -*- coding: utf-8 -*-
from google.appengine.ext import db

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


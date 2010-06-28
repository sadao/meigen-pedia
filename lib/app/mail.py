# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '../../')

import logging
import re
from models import Account
from viewer import Viewer
from email.header import decode_header
from google.appengine.api import mail,users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

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


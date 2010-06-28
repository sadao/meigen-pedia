# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from lib.portal import index,meigen,person,rss
from lib.app import settings,mail
from lib.app.index import AppIndexHandler
from lib.app.meigen import AppMeigenHandler
from lib.app.person import AppPersonHandler
import urls

# webapp フレームワークのURLマッピングです
application = webapp.WSGIApplication([
                (urls.PORTAL_INDEX_URL, index.PortalIndexHandler),
                (urls.PORTAL_MEIGEN_URL, meigen.PortalMeigenHandler),
                (urls.PORTAL_PERSON_URL, person.PortalPersonHandler),
                (urls.APP_INDEX_URL, AppIndexHandler),
                (urls.APP_MEIGEN_URL, AppMeigenHandler),
                (urls.APP_PERSON_URL, AppPersonHandler),
                (urls.APP_SETTINGS_URL, settings.AppSettingsHandler),
                (urls.RSS_URL, rss.RssHandler),
                mail.MailHandler.mapping(),
              ], debug=True)

# WebApp フレームワークのメインメソッドです
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
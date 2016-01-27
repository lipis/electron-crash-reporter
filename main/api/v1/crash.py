# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
from flask.ext import restful
import flask

from api import helpers
import auth
import model
import util

from main import api_v1


@api_v1.resource('/crash/', endpoint='api.crash.list')
class CrashListAPI(restful.Resource):
  def get(self):
    crash_dbs, crash_cursor = model.Crash.get_dbs()
    return helpers.make_response(crash_dbs, model.Crash.FIELDS, crash_cursor)


@api_v1.resource('/crash/<string:crash_key>/', endpoint='api.crash')
class CrashAPI(restful.Resource):
  def get(self, crash_key):
    crash_db = ndb.Key(urlsafe=crash_key).get()
    if not crash_db:
      helpers.make_not_found_exception('Crash %s not found' % crash_key)
    return helpers.make_response(crash_db, model.Crash.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/crash/', endpoint='api.admin.crash.list')
class AdminCrashListAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    crash_keys = util.param('crash_keys', list)
    if crash_keys:
      crash_db_keys = [ndb.Key(urlsafe=k) for k in crash_keys]
      crash_dbs = ndb.get_multi(crash_db_keys)
      return helpers.make_response(crash_dbs, model.crash.FIELDS)

    crash_dbs, crash_cursor = model.Crash.get_dbs()
    return helpers.make_response(crash_dbs, model.Crash.FIELDS, crash_cursor)


@api_v1.resource('/admin/crash/<string:crash_key>/', endpoint='api.admin.crash')
class AdminCrashAPI(restful.Resource):
  @auth.admin_required
  def get(self, crash_key):
    crash_db = ndb.Key(urlsafe=crash_key).get()
    if not crash_db:
      helpers.make_not_found_exception('Crash %s not found' % crash_key)
    return helpers.make_response(crash_db, model.Crash.FIELDS)

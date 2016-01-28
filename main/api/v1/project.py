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


@api_v1.resource('/project/', endpoint='api.project.list')
class ProjectListAPI(restful.Resource):
  @auth.login_required
  def get(self):
    project_dbs, project_cursor = model.Project.get_dbs(user_key=auth.current_user_key())
    return helpers.make_response(project_dbs, model.Project.FIELDS, project_cursor)


@api_v1.resource('/project/<string:project_key>/', endpoint='api.project')
class ProjectAPI(restful.Resource):
  @auth.login_required
  def get(self, project_key):
    project_db = ndb.Key(urlsafe=project_key).get()
    if not project_db or project_db.user_key != auth.current_user_key():
      helpers.make_not_found_exception('Project %s not found' % project_key)
    return helpers.make_response(project_db, model.Project.FIELDS)


###############################################################################
# Admin
###############################################################################
@api_v1.resource('/admin/project/', endpoint='api.admin.project.list')
class AdminProjectListAPI(restful.Resource):
  @auth.admin_required
  def get(self):
    project_keys = util.param('project_keys', list)
    if project_keys:
      project_db_keys = [ndb.Key(urlsafe=k) for k in project_keys]
      project_dbs = ndb.get_multi(project_db_keys)
      return helpers.make_response(project_dbs, model.project.FIELDS)

    project_dbs, project_cursor = model.Project.get_dbs()
    return helpers.make_response(project_dbs, model.Project.FIELDS, project_cursor)


@api_v1.resource('/admin/project/<string:project_key>/', endpoint='api.admin.project')
class AdminProjectAPI(restful.Resource):
  @auth.admin_required
  def get(self, project_key):
    project_db = ndb.Key(urlsafe=project_key).get()
    if not project_db:
      helpers.make_not_found_exception('Project %s not found' % project_key)
    return helpers.make_response(project_db, model.Project.FIELDS)

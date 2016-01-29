# coding: utf-8

from flask.ext import wtf
from google.appengine.ext import ndb
import flask
import wtforms

import auth
import config
import model
import util

from main import app


###############################################################################
# Update
###############################################################################
class ProjectUpdateForm(wtf.Form):
  name = wtforms.StringField(
    model.Project.name._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  token = wtforms.StringField(
    model.Project.token._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
  )


@app.route('/project/create/', methods=['GET', 'POST'])
@app.route('/project/<int:project_id>/update/', methods=['GET', 'POST'])
@auth.login_required
def project_update(project_id=0):
  if project_id:
    project_db = model.Project.get_by_id(project_id)
  else:
    project_db = model.Project(user_key=auth.current_user_key())

  if not project_db or project_db.user_key != auth.current_user_key():
    flask.abort(404)

  form = ProjectUpdateForm(obj=project_db)

  if form.validate_on_submit():
    form.populate_obj(project_db)
    project_db.put()
    return flask.redirect(flask.url_for('project_view', project_id=project_db.key.id()))

  return flask.render_template(
    'project/project_update.html',
    title=project_db.name if project_id else 'New Project',
    html_class='project-update',
    form=form,
    project_db=project_db,
  )


###############################################################################
# List
###############################################################################
@app.route('/project/')
@auth.login_required
def project_list():
  project_dbs, project_cursor = model.Project.get_dbs(user_key=auth.current_user_key())
  return flask.render_template(
    'project/project_list.html',
    html_class='project-list',
    title='Projects',
    project_dbs=project_dbs,
    next_url=util.generate_next_url(project_cursor),
    api_url=flask.url_for('api.project.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/project/<int:project_id>/')
@auth.login_required
def project_view(project_id):
  project_db = model.Project.get_by_id(project_id)
  if not project_db or project_db.user_key != auth.current_user_key():
    flask.abort(404)

  crash_dbs, crash_cursor = project_db.get_crash_dbs(
      order=util.param('order') or '-created',
    )

  return flask.render_template(
    'project/project_view.html',
    html_class='project-view',
    title=project_db.name,
    project_db=project_db,
    crash_dbs=crash_dbs,
    next_url=util.generate_next_url(crash_cursor),
    api_url=flask.url_for('api.project', project_key=project_db.key.urlsafe() if project_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/project/')
@auth.admin_required
def admin_project_list():
  project_dbs, project_cursor = model.Project.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'project/admin_project_list.html',
    html_class='admin-project-list',
    title='Projects',
    project_dbs=project_dbs,
    next_url=util.generate_next_url(project_cursor),
    api_url=flask.url_for('api.admin.project.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class ProjectUpdateAdminForm(ProjectUpdateForm):
  pass


@app.route('/admin/project/create/', methods=['GET', 'POST'])
@app.route('/admin/project/<int:project_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_project_update(project_id=0):
  if project_id:
    project_db = model.Project.get_by_id(project_id)
  else:
    project_db = model.Project(user_key=auth.current_user_key())

  if not project_db:
    flask.abort(404)

  form = ProjectUpdateAdminForm(obj=project_db)

  if form.validate_on_submit():
    form.populate_obj(project_db)
    project_db.put()
    return flask.redirect(flask.url_for('admin_project_list', order='-modified'))

  return flask.render_template(
    'project/admin_project_update.html',
    title=project_db.name,
    html_class='admin-project-update',
    form=form,
    project_db=project_db,
    back_url_for='admin_project_list',
    api_url=flask.url_for('api.admin.project', project_key=project_db.key.urlsafe() if project_db.key else ''),
  )

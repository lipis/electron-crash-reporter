# coding: utf-8

from flask.ext import wtf
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
import cloudstorage
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
class CrashUpdateForm(wtf.Form):
  ver = wtforms.StringField(
    model.Crash.ver._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  platform = wtforms.StringField(
    model.Crash.platform._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  process_type = wtforms.StringField(
    model.Crash.process_type._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  guid = wtforms.StringField(
    model.Crash.guid._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  version = wtforms.StringField(
    model.Crash.version._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
    description='The version in package.json.',
  )
  productName = wtforms.StringField(
    model.Crash.productName._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
    description='The product name in the crashReporter options object.',
  )
  prod = wtforms.StringField(
    model.Crash.prod._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
    description='Name of the underlying product. In this case Electron.',
  )
  companyName = wtforms.StringField(
    model.Crash.companyName._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
    description='The company name in the crashReporter options object.',
  )

  upload_file_minidump = wtforms.FileField(
    'File',
    [wtforms.validators.required()],
  )


@app.route('/crash/create/', methods=['GET', 'POST'])
@app.route('/crash/<int:crash_id>/update/', methods=['GET', 'POST'])
def crash_update(crash_id=0):
  if crash_id:
    crash_db = model.Crash.get_by_id(crash_id)
  else:
    crash_db = model.Crash()

  if not crash_db:
    flask.abort(404)

  form = CrashUpdateForm(csrf_enabled=False, obj=crash_db)

  if form.validate_on_submit():
    form.version.data = util.param('_version') or form.version.data
    form.productName.data = util.param('_productName') or form.productName.data
    form.companyName.data = util.param('_companyName') or form.companyName.data
    form.populate_obj(crash_db)

    file_data = flask.request.files[form.upload_file_minidump.name].read()
    blob_key = create_file(form.guid.data, file_data)
    crash_db.blob_key = blob_key
    crash_db.put()
    return '200'

  return flask.render_template(
    'crash/crash_update.html',
    title=crash_db.guid if crash_id else 'New Crash',
    html_class='crash-update',
    form=form,
    crash_db=crash_db,
  )


def create_file(name, data):
  filename = '/%s/%s' % (config.CONFIG_DB.bucket_name, name)
  with cloudstorage.open(filename, 'w', content_type='text/plain') as f:
    f.write(data)

  # Blobstore API requires extra /gs to distinguish against blobstore files.
  blobstore_filename = '/gs' + filename
  return ndb.BlobKey(blobstore.create_gs_key(blobstore_filename))


###############################################################################
# List
###############################################################################
@app.route('/crash/')
def crash_list():
  crash_dbs, crash_cursor = model.Crash.get_dbs()
  return flask.render_template(
    'crash/crash_list.html',
    html_class='crash-list',
    title='Crash List',
    crash_dbs=crash_dbs,
    next_url=util.generate_next_url(crash_cursor),
    api_url=flask.url_for('api.crash.list'),
  )


###############################################################################
# View
###############################################################################
@app.route('/crash/<int:crash_id>/')
def crash_view(crash_id):
  crash_db = model.Crash.get_by_id(crash_id)
  if not crash_db:
    flask.abort(404)

  return flask.render_template(
    'crash/crash_view.html',
    html_class='crash-view',
    title=crash_db.guid,
    crash_db=crash_db,
    api_url=flask.url_for('api.crash', crash_key=crash_db.key.urlsafe() if crash_db.key else ''),
  )


###############################################################################
# Admin List
###############################################################################
@app.route('/admin/crash/')
@auth.admin_required
def admin_crash_list():
  crash_dbs, crash_cursor = model.Crash.get_dbs(
    order=util.param('order') or '-modified',
  )
  return flask.render_template(
    'crash/admin_crash_list.html',
    html_class='admin-crash-list',
    title='Crash List',
    crash_dbs=crash_dbs,
    next_url=util.generate_next_url(crash_cursor),
    api_url=flask.url_for('api.admin.crash.list'),
  )


###############################################################################
# Admin Update
###############################################################################
class CrashUpdateAdminForm(CrashUpdateForm):
  pass


@app.route('/admin/crash/create/', methods=['GET', 'POST'])
@app.route('/admin/crash/<int:crash_id>/update/', methods=['GET', 'POST'])
@auth.admin_required
def admin_crash_update(crash_id=0):
  if crash_id:
    crash_db = model.Crash.get_by_id(crash_id)
  else:
    crash_db = model.Crash()

  if not crash_db:
    flask.abort(404)

  form = CrashUpdateAdminForm(obj=crash_db)

  if form.validate_on_submit():
    form.populate_obj(crash_db)
    crash_db.put()
    return flask.redirect(flask.url_for('admin_crash_list', order='-modified'))

  return flask.render_template(
    'crash/admin_crash_update.html',
    title='%s' % crash_db.guid if crash_id else 'New Crash',
    html_class='admin-crash-update',
    form=form,
    crash_db=crash_db,
    back_url_for='admin_crash_list',
    api_url=flask.url_for('api.admin.crash', crash_key=crash_db.key.urlsafe() if crash_db.key else ''),
  )

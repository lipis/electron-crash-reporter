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
  )
  productName = wtforms.StringField(
    model.Crash.productName._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
  )
  prod = wtforms.StringField(
    model.Crash.prod._verbose_name,
    [wtforms.validators.required()],
    filters=[util.strip_filter],
  )
  companyName = wtforms.StringField(
    model.Crash.companyName._verbose_name,
    [wtforms.validators.optional()],
    filters=[util.strip_filter],
  )
  upload_file_minidump = wtforms.FileField(
    'File',
    [wtforms.validators.required()],
  )


@app.route('/create/', methods=['GET', 'POST'])
def crash_create():
  crash_db = model.Crash()

  if not crash_db:
    flask.abort(404)

  form = CrashUpdateForm(csrf_enabled=False, obj=crash_db)

  if form.validate_on_submit():
    form.version.data = util.param('_version') or form.version.data
    form.productName.data = util.param('_productName') or form.productName.data
    form.companyName.data = util.param('_companyName') or form.companyName.data
    if not form.version.data:
      form.version.errors.append('This field is required.')
    if not form.productName.data:
      form.productName.errors.append('This field is required.')
    if not form.companyName.data:
      form.companyName.errors.append('This field is required.')

    if not form.errors:
      form.populate_obj(crash_db)
      file_data = flask.request.files[form.upload_file_minidump.name].read()
      blob_key = create_file(form.guid.data, file_data)
      crash_db.blob_key = blob_key
      crash_db.put()
      return '200'

  return flask.render_template(
    'crash/crash_update.html',
    title='New Crash',
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
# Admin List
###############################################################################
@app.route('/admin/crash/')
@auth.admin_required
def admin_crash_list():
  crash_dbs, crash_cursor = model.Crash.get_dbs(
    order=util.param('order') or '-created',
  )
  return flask.render_template(
    'crash/admin_crash_list.html',
    html_class='admin-crash-list',
    title='Crash List',
    crash_dbs=crash_dbs,
    next_url=util.generate_next_url(crash_cursor),
    api_url=flask.url_for('api.admin.crash.list'),
  )

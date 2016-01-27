# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask

from api import fields
import model


class Crash(model.Base):
  ver = ndb.StringProperty(required=True, verbose_name=u'Electron Version')
  platform = ndb.StringProperty(required=True)
  process_type = ndb.StringProperty(required=True)
  guid = ndb.StringProperty(required=True, verbose_name=u'GUID')
  version = ndb.StringProperty(required=True, verbose_name=u'App Version')
  productName = ndb.StringProperty(required=True, verbose_name=u'Product Name')
  prod = ndb.StringProperty(default='Electron', required=True, verbose_name=u'Underlying Product')
  companyName = ndb.StringProperty(required=True, verbose_name=u'Company Name')
  blob_key = ndb.BlobKeyProperty()

  @property
  def serve_url(self):
    return '%s/serve/%s' % (flask.request.url_root[:-1], self.blob_key)


  FIELDS = {
    'ver': fields.String,
    'platform': fields.String,
    'process_type': fields.String,
    'guid': fields.String,
    'version': fields.String,
    'productName': fields.String,
    'prod': fields.String,
    'companyName': fields.String,
  }

  FIELDS.update(model.Base.FIELDS)

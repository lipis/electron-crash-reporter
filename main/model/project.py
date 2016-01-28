# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb

from api import fields
import model


class Project(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  name = ndb.StringProperty(required=True)
  token = ndb.StringProperty(default='')

  def get_crash_dbs(self, **kwargs):
    return model.Crash.get_dbs(project_key=self.key, **kwargs)

  FIELDS = {
    'user_key': fields.Key,
    'name': fields.String,
    'token': fields.String,
  }

  FIELDS.update(model.Base.FIELDS)

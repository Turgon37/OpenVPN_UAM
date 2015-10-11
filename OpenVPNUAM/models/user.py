# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
#
# Copyright (c) 2015 Thomas PAJON, Pierre GINDRAUD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Models/User

This file contains the class of Users entities
"""

# System imports
import datetime
import logging

# Project imports
from .hostname import Hostname
from ..helpers import *

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.model.user')


class User(object):
  """Build an instance of the user program class
  """

  def __init__(self, cuid, mail):
    """Constructor: Build a new empty user

    @param cuid [str] : common unique user identifier
    @param mail [str] : main mail address of this user
    """
    # database model
    self._id = None
    self._cuid = cuid
    self._user_mail = mail
    self._certificate_mail = None
    self._password_mail = None
    self._is_enabled = False
    self._certificate_password = None
    self._start_time = None
    self._stop_time = None
    self._creation_time = datetime.datetime.today()
    self._update_time = None
    # python model
    # This is the list of current user's hostname
    self.__lst_hostname = []
    # This is the reference to the main database class
    # it is used to perform self object update call
    # Exemple if you want to update a attribut of an instance of this class
    # like one of theses above, you will need to call the main database to store
    # change into database engine
    self.__db = None

# INIT API
  def load(self, attributs, hostnames=[]):
    """Load an user entity with the given list of attributes and hostnames

    @param attributs [dict] : a key-value dict which contains attributs
    to set to this User object
    """
    assert isinstance(attributs, dict)
    # already set
    assert self._id is None
    # loop for each given attributes
    for key in attributs:
      if hasattr(self, "_" + key):
        setattr(self, "_" + key, attributs[key])
      else:
        g_sys_log.error('Unknown attribute from source "' + key + '"')

    # load hostnames
    assert isinstance(hostnames, list)
    self.__lst_hostname = hostnames

# Getters methods
  def __getattr__(self, key):
    """Upgrade default getter to allow get semi-private attributes
    """
    try:
      return object.__getattribute__(self, "_" + key)
    except AttributeError:
      pass
    return object.__getattribute__(self, key)

  def getHostnameList(self):
    """Get the list of the user's hostname

    @return [list] : list of hostnames used by the user
    """
    return self.__lst_hostname

  def getEnabledHostnameList(self):
    """Get the list of the user's hostname which are enabled

    @return [list<Hostname>] : list of enabled hostnames used by the user
    """
    l_host = []
    for host in self.__lst_hostname:
      if host.is_enabled:
        l_host.append(host)
    return l_host

  @property
  def db(self):
    """Return the db instance associated with this user

    @return [Database] the database reference
    """
    assert self.__db is not None
    return self.__db

# Setters methods
  def __setattr__(self, key, value):
    """Upgrade default setter to trigger database update
    """
    # update concerns a Model's attribut
    if hasattr(self, "_" + key):
      setattr(self, "_" + key, value)
      self.db.update(key, value, self, 1)
    else:
      return object.__setattr__(self, key, value)

  @db.setter
  def db(self, db):
    """Set the internal DB link to allow self update

    Add reference to main database into this user and all his hostname
    @param db [Database] : the database instance to use for self update call
    """
    assert self.__db is None
    self.__db = db
    for h in self.__lst_hostname:
      h.db = db

# API methods
  def enable(self):
    """Disable the current user

    Call the update routine to perform the change in database
    """
    if self._is_enabled:
      g_sys_log.warning("User (%d) '%s' already enabled",
                        self.id,
                        self.cuid)
      # TODO data consistency
    else:
      g_sys_log.info("Enable user (%d) '%s'",
                     self.id,
                     self.cuid)
      self.is_enabled = True

  def disable(self):
    """Enable the current user

    Call the update routine to perform the change in database
    """
    if not self._is_enabled:
      # TODO data consistency
      g_sys_log.warning("User (%d) '%s' already disabled",
                        self.id,
                        self.cuid)
    else:
      g_sys_log.info("Disable user (%d) '%s'",
                     self.id,
                     self.cuid)
      self.is_enabled = False

# DEBUG methods
  def __str__(self):
    """[DEBUG] Produce a description string for this user instance

    @return [str] a formatted string that describe this user
    """
    content = ("USER (" + str(self.id) + ")" +
               "\n  CUID = " + str(self.cuid) +
               "\n  UMAIL = " + str(self.user_mail) +
               "\n  CERTMAIL = " + str(self.certificate_mail) +
               "\n  PASSMAIL = " + str(self.password_mail) +
               "\n  STATUS = " + str(self.is_enabled) +
               "\n  CERT PASSWD = " + str(self.certificate_password) +
               "\n  START DATE = " + str(self.start_time) +
               "\n  END DATE = " + str(self.stop_time) +
               "\n  CREATED ON = " + str(self.creation_time) +
               "\n  UPDATED ON = " + str(self.update_time))
    for h in self.__lst_hostname:
      content += "\n" + str(h)
    return content

  def __repr__(self):
    """[DEBUG] Produce a list of attribute as string for this user instance

    @return [str] a formatted string that describe this user
    """
    return ("[id(" + str(self.id) + ")," +
            " cuid(" + str(self.cuid) + ")," +
            " umail(" + str(self.user_mail) + ")," +
            " certmail(" + str(self.certificate_mail) + ")," +
            " passmail(" + str(self.password_mail) + ")," +
            " enable(" + str(self.is_enabled) + ")," +
            " certpasswd(" + str(self.certificate_password) + ")," +
            " startdate(" + str(self.start_time) + ")," +
            " enddate(" + str(self.stop_time) + ")," +
            " createdon(" + str(self.creation_time) + ")," +
            " updatedon(" + str(self.update_time) + ")," +
            " hostname(" + str(len(self.__lst_hostname)) + ")]")

# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
#
# Copyright (c) 2015 Thomas PAJON
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

"""Models/Certificate

This file contains class for certificate.
It provide some function to manage this certificate and also to update its
attributs.
"""

# System imports
import datetime
import logging

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.model.certificate')


class Certificate(object):
  """Constructor: Build an instanceof the certificate program class
  """

  def __init__(self, begin, end):
    """Constructor: Build a new empty certificate
    """
    # database model
    self._id = None
    self._is_password = False
    self._revoked_reason = None
    self._revoked_time = None
    self._certificate_begin_time = begin
    self._certificate_end_time = end
    # This is the reference to the main database class
    # it is used to perform self object update call
    # Exemple if you want to update a attribut of an instance of this class
    # like one of theses above, you will need to call the main database to
    # store change into database engine
    self.__db = None

  def load(self, attributes):
    """Load a certificate entity with attributes

    @param attributes [dict] : a key-value dict which contains attributs
    to set to this Certificate object
    """
    assert self._id is None
    assert isinstance(attributes, dict)
    # loop for each given attributes
    for key in attributes:
      if hasattr(self, "_" + key):
        setattr(self, "_" + key, attributes[key])
      else:
        g_sys_log.error('Unknown attribute from source "' + key + '"')

# Getters methods
  def __getattr__(self, key):
    """Upgrade default getter to allow get semi-private attributes
    """
    try:
      return object.__getattribute__(self, "_" + key)
    except AttributeError:
      pass
    return object.__getattribute__(self, key)

  def getValidityDuration(self):
    """Calculate the validity duration of a certificate

    @return [datetime.datetime] : validity duration of the certificate
    """
    return self.certificate_end_time - self.certificate_begin_time

  @property
  def db(self):
    """Return the db instance associated with this certificate

    @return [Database] the database reference
    """
    assert self.__db is not None
    return self.__db

# Setters methods
  @db.setter
  def db(self, db):
    """Set the internal DB link to allow self update

    Add reference to main database into this user and all his hostname
    @param db [Database] : the database instance to use for self update call
    """
    assert self.__db is None
    self.__db = db

# DEBUG methods
  def __str__(self):
    """[DEBUG] Produce a description string for this certificate instance

    @return [str] a formatted string that describe this certificate
    """
    content = ("CERTIFICAT (" + str(self.id) + ")" +
               "\n      IS_PASSWORD = " + str(self.is_password) +
               "\n      REVOKED REASON = " + str(self.revoked_reason) +
               "\n      REVOKED TIME = " + str(self.revoked_time) +
               "\n      NOT BEFORE = " + str(self.certificate_begin_time) +
               "\n      NOT AFTER = " + str(self.certificate_end_time))
    return content

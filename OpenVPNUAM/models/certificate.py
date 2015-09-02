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

  def __init__(self):
    """Constructor: Build a new empty certificate
    """
    # database model
    self._id = None
    self._is_password = True
    self._revoked_reason = None
    self._revoked_time = None
    self._certificate_begin_time = None
    self._certificate_end_time = None
    # This is the reference to the main database class
    # it is used to perform self object update call
    # Exemple if you want to update a attribut of an instance of this class
    # like one of theses above, you will need to call the main database to store
    # change into database engine
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
  def getBeginTime(self):
    """Return the NOT BEFORE time of this certificate
    
    @return [datetime.datetime] The time at which the certificate will become
    valid
    """
    return self._certificate_begin_time

  def getEndTime(self):
    """Return the NOT AFTER time of this certificate
  
    @return [datetime.datetime] The time at which the certificate will become
    expired
    """
    return self._certificate_end_time

# Setters methods
  def setDb(self, db):
    """Set the internal DB link to allow self update

    Add reference to main database into this hostname
    @param db [Database] : the database instance to use for self update call
    """
    assert self.__db is None
    self.__db = db

# utilities methods
  def __str__(self):
    """[DEBUG] Produce a description string for this certificate instance

    @return [str] a formatted string that describe this certificate
    """
    content = ("CERTIFICAT (" + str(self._id) + ")" +
               "\n      IS_PASSWORD = " + str(self._is_password) +
               "\n      REVOKED REASON = " + str(self._revoked_reason) +
               "\n      REVOKED TIME = " + str(self._revoked_time) +
               "\n      NOT BEFORE = " + str(self._certificate_begin_time) +
               "\n      NOT AFTER = " + str(self._certificate_end_time))
    return content
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

"""Models/Hostname

This file contains class for hostname.
It provide some function to manage this hostname and also to update
its attributes.
"""

# System imports
import datetime
import logging

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.model.hostname')


class Hostname(object):
  """Build an instance of the hostname program class
  """

  def __init__(self, name):
    """Constructor: Build a new empty hostname

    @param name [str] : the name of the hostname
    """
    # database model
    self._id = None
    self._name = name
    self._is_enabled = False
    self._is_online = False
    self._creation_time = datetime.datetime.today()
    self._update_time = None
    # python model
    self.__lst_certificate = []
    # internal link to database for self update
    self.__db = None

  def load(self, attributs):
    """Load an hostname entity with attributs

    @param attributs [dict] : a key-value dict which contains attributs
    to set to this Hostname object
    """
    assert self._id is None
    assert isinstance(attributs, dict)
    # loop for each given attributes
    for key in attributs:
      if hasattr(self, "_" + key):
        setattr(self, "_" + key, attributs[key])
      else:
        g_sys_log.error('Unknown attribute from source "' + key + '"')

# Getters methods
  def getName(self):
    """Get name of this hostname

    @return [str] : the name of the hostname
    """
    return self._name

  def getCreationTime(self):
    """Get the creation of the hostname

    @return [datetime] : the creation date of the hostname
    """
    return self._creation_time

  def getUpdateTime(self):
    """getDateUpdate(): Get the date of the last update of
    the hostname

    @return [datetime] : date of the last update of the hostname
    """
    return self._update_time

  def getActivationState(self):
    """getActivationState(): get the activation state of the
    hostname

    @return [bool] : the activation state of the hostname
    """
    return self._is_enabled

  def getStatus(self):
    """getStatus(): Get if the hostname is online

    @return [bool] : status of the hostname
    """
    return self._is_online

# Setters methods
  def setName(self, name):
    """setName(): Change the name of the hostname

    @param name [str] : name of the hostname
    """
    self._name = name
    self.__update()

  def setDb(self, db):
    """Set the internal DB link to allow self update

    Add reference to main database into this hostname
    @param db [Database] : the database instance to use for self update call
    """
    assert self.__db is None
    self.__db = db

# Private methods
  def __update(self):
    """update(): Change the date of the last update of the
    hostname
    """
    self._update_time = datetime.datetime.today()

  def enable(self):
    """enable(): Set hostname enable
    """
    self._is_enable = True
    self.__update()

  def disable(self):
    """disable(): Set hostname disable
    """
    self._is_enabled = False
    self.__update()

  def setOnline(self):
    """setOnline(): Change the status of the hostname to
    online
    """
    self._is_online = True
    self.__update()

  def setOffline(self):
    """setOffline(): Change the status of the hostname to
    offline
    """
    self._is_online = False
    self.__update()

  def __str__(self):
    """[DEBUG] Produce a description string for this user instance

    @return [str] a formatted string that describe this user
    """
    content = ("  HOSTNAME (" + str(self._id) + ")" +
               "\n    NAME = " + str(self._name) +
               "\n    STATUS = " + str(self._is_enabled) +
               "\n    ONLINE STATUS = " + str(self._is_online) +
               "\n    CREATED ON = " + str(self._creation_time) +
               "\n    UPDATED ON = " + str(self._update_time))
    for c in self.__lst_certificate:
      content += str(c)
    return content

  def __repr__(self):
    """[DEBUG] Produce a list of attribute as string for this hostname instance

    @return [str] a formatted string that describe this hostname
    """
    return ("[id(" + str(self._id) + ")," +
            " name(" + str(self._name) + ")," +
            " enable(" + str(self._is_enabled) + ")," +
            " createdon(" + str(self._creation_time) + ")," +
            " updatedon(" + str(self._update_time) + ")," +
            " certificate(" + str(len(self.__lst_certificate)) + ")]")

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


class Hostname:
  """Build an instance of the hostname program class
  """

  def __init__(self, name):
    """Constructor: Build a new empty hostname

    @param name [str] : the name of the hostname
    """
    # database model
    self.__id = None
    self.__name = name
    self.__is_enable = False
    self.__is_online = False
    self.__creation_time = datetime.datetime.today()
    self.__update_time = None
    # python model
    self.__lst_certificate = []

# Getters methods
  def getName(self):
    """Get name of this hostname

    @return [str] : the name of the hostname
    """
    return self.__name

  def getDateCreation(self):
    """Get the creation of the hostname

    @return [datetime] : the creation date of the hostname
    """
    return self.__date_creation

  def getDateUpdate(self):
    """getDateUpdate(): Get the date of the last update of
    the hostname

    @return [datetime] : date of the last update of the hostname
    """
    return self.__date_update

  def getActivationState(self):
    """getActivationState(): get the activation state of the
    hostname

    @return [boolean] : the activation state of the hostname
    """
    return self.__is_enable

  def getStatus(self):
    """getStatus(): Get if the hostname is online

    @return [boolean] : status of the hostname
    """
    return self.__is_online

# Setters methods

  def setName(self, name):
    """setName(): Change the name of the hostname

    @param name [str] : name of the hostname
    """
    self.__name = name
    self.__update()

  def __update(self):
    """update(): Change the date of the last update of the
    hostname
    """
    self.__date_update = datetime.today()

  def enable(self):
    """enable(): Set hostname enable
    """
    self.__is_enable = True
    self.__update()

  def disable(self):
    """disable(): Set hostname disable
    """
    self.__is_enable = False
    self.__update()

  def setOnline(self):
    """setOnline(): Change the status of the hostname to
    online
    """
    self.__is_online = True
    self.__update()

  def setOffline(self):
    """setOffline(): Change the status of the hostname to
    offline
    """
    self.__is_online = False
    self.__update()
    
    
  def toString(self):
    """[DEBUG] Produce a description string for this user instance
    
    @return [str] a formatted string that describe this user
    """
    content = ("  HOSTNAME (" + str(self.__id) + ")" +
              "\n    NAME = " + str(self.__name) +
              "\n    STATUS = " + str(self.__is_enable) +
              "\n    ONLINE STATUS = " + str(self.__is_online) +
              "\n    CREATED ON = " + str(self.__creation_time) +
              "\n    UPDATED ON = " + str(self.__update_time))
    for c in self.__lst_certificate:
      content += c.toString()
    return content
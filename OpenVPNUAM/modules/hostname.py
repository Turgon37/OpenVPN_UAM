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

"""HOSTNAME - Hostname program class

This program class is the model that define a hostname. It allows to manage this 
hostname and also to update its attributes.
"""

# System imports
import datetime


class Hostname:
  """Build an instance of the hostname program class
  """

  def __init__(self, name, date_creation = datetime.today(),
                      date_update = datetime.today(), is_enable = True,
                      is_online = False):
    """Constructor: Build the program lead class

    @param name [str] : the name of the hostname
    @param date_creation [datetime] : date on which the hostname was created
    @param date_update [datetime] : date of the last hostname update
    @param is_enable [boolean] : if the hostname is activated
    @param is_online [boolean] : if the hostname is online
    """
    self.__name = name
    self.__date_creation = date_creation
    self.__date_update = date_update
    self.__is_enable = is_enable
    self.__is_online = is_online

  """Getters methods
  """

  def getName(self):
    """getName(): Get name of this hostname

    @return [str] : the name of the hostname
    """
    return self.__name

  def getDateCreation(self):
    """getDateCreation(): Get the creation of the hostname

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

  """Setters methods
  """

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
    """ --Change the datetime in the Database-- """
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

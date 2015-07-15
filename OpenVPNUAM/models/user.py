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

# Project imports 
from .hostname import Hostname

class User:
  """Build an instance of the user program class
  """

  def __init__(self, cuid, mail):
    """Constructor: Build a new empty user
    
    @param cuid [str] : common unique user identifier
    @param mail [str] : main mail address of this user
    """
    # database model
    self.__id = None
    self.__cuid = cuid
    self.__user_mail = mail
    self.__certificate_mail = None
    self.__pasword_mail = None
    self.__is_enable = False
    self.__certificate_password = None
    self.__user_start_date = None
    self.__user_stop_time = None
    self.__creation_time = datetime.datetime.today()
    self.__update_time = None
    # python model
    self.__lst_hostname = []

# Getters methods
  def getHostname(self):
    """Get the list of the user's hostname

    @return [list] : list of hostnames used by the user
    """
    return self.__lst_hostname

# Setters methods
  def addHostname(self, hostname):
    """addHostname(): Add an hostname to the user

    @param hostname [Hostname] : an hostname will be used by the user
    """
    if not isinstance(hostname, Hostname):
      print("TODO INTERNAL ERROR")
      return 
    self.__lst_hostname.append(hostname)
    """ --Add the entry in the Database-- """

  def enable(self):
    """enable(): Change the state of the user to enabled
    """
    if self.__is_enable == True:
      print("TODO INTERNAL ERROR")
      return
    self.__is_enable = True

  def disable(self):
    """disable(): Change the state of the user to disabled
    """
    if self.__is_enable == False:
      print("TODO INTERNAL ERROR")
      return
    self.__is_enable = False

  def toString(self):
    """[DEBUG] Produce a description string for this user instance
    
    @return [str] a formatted string that describe this user
    """
    content = ("USER (" + str(self.__id) + ")" +
              "\n  CUID = " + str(self.__cuid) +
              "\n  UMAIL = " + str(self.__user_mail) +
              "\n  CERTMAIL = " + str(self.__certificate_mail) +
              "\n  PASSMAIL = " + str(self.__pasword_mail) +
              "\n  STATUS = " + str(self.__is_enable) +
              "\n  CERT PASSWD = " + str(self.__certificate_password) +
              "\n  START DATE = " + str(self.__user_start_date) +
              "\n  END DATE = " + str(self.__user_stop_time) +
              "\n  CREATED ON = " + str(self.__creation_time) +
              "\n  UPDATED ON = " + str(self.__update_time))
    for h in self.__lst_hostname:
      content += "\n" + h.toString()
    return content
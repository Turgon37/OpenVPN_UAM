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

"""USER - user program class

This program class is the model that define an user. It allows to manage this
user and also to update its attributes.
"""

# System imports
import .hostname

class User:
  """Build an instance of the user program class
  """

  def __init__(self, mail, is_enable = True):
    """Constructor: Build the program lead program

    @param mail [string] : first e-mail address that the user has
    @param is_enable [boolean] : if the user is activated
    """
    self.__lst_hostname = []
    self.__lst_mail = [mail]
    self.__is_enable = is_enable

  """Getters methods
  """

  def getHostname(self):
    """getHostname(): Get the list of the user's hostname

    @return [list] : list of hostnames used by the user
    """
    return self.__lst_hostname

  def getMail(self):
    """getMail(): Get the list of the user's e-mail address

    @return [list] : list of e-mail address used by the user
    """
    return self.__lst_mail

  def getActivationState(self):
    """getActivatedState(): Get the state of the user

    @return [boolean] : if the user is enable
    """
    return self.__is_enable

  """Setters methods
  """

  def addHostname(self, hostname):
    """addHostname(): Add an hostname to the user

    @param hostname [str] : an hostname will be used by the user
    """
    self.__lst_hostname.append(hostname.Hostname(hostname))
    """ --Add the entry in the Database-- """

  def removeHostname(self, hostname):
    """removeHostname(): Remove an hostname to the user

    @param hostname [str] : an hostname used by the user
    """
    """ --Revoke certificates related on this hostname-- """
    for hostn in self.__lst_hostname:
      if hostn.getName() == hostname:
        self.__lst_hostname.remove(hostn)
    """ --Delete all entries related on this hostname in the Database-- """

  def addMail(self, mail):
    """addMail(): Add an e-mail address to the user

    @param mail [str] : an e-mail will be used by the user
    """
    self.__lst_mail.append(mail)
    """ --Add the entry in the Database-- """

  def removeMail(self, mail):
    """removeMail(): Remove an e-mail address to the user

    @param mail [str] : an e-mail address used by the user
    """
    self.__lst_mail.remove(mail)
    """ --Delete the entry in the database-- """

  def enable(self):
    """enable(): Change the state of the user to enable
    """
    self.__is_enable = True
    """ --Change the entry value in the database-- """

  def disable(self):
    """disable(): Change the state of the user to disable
    """
    self.__is_enable = False
    """ --Change the entry value in the database-- """

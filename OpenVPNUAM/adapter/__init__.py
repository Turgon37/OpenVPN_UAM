# -*- coding: utf8 -*-

# This file is a part of OpenVPN-UAM
#
# Copyright (c) 2015 Pierre GINDRAUD
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

"""This file provide the base class that must be extended by all database
adapter
"""

# Project imports
from .. import models as Model
from ..helpers import *


class Adapter(object):
  """This is an abstract class that describe a basic database adapter"""

  # constant for adapter connection types
  TYPE_LOCAL = 0
  TYPE_REMOTE = 1

  # mysql connection status
  STATUS_CLOSE = 0
  STATUS_OPEN = 1

  def __init__(self, name, type):
    """You must call it in your adapter __init__

    This init must be call in the begining of your adapter extended init()
    @param name [str] the name of the adapter technology. This name must
    match the .py file in which the code is stored
    @param type [integer] the connection type of the adapter is use.
    see constants above for other details
    """
    self.__name = name
    self.__type = type

  @property
  def name(self):
    """Return the name of this adapter

    @return [str] the name of this adapter
    """
    return self.__name

  @property
  def type(self):
    """Return the type of this adapter

    @return [integer] the Adapter constants that describe the type
    """
    return self.__type

  def load(self, config):
    """This function must be overloaded

    Make here all your database adapter configuration checking, error here are
    only relative to adapter configuration mistake
    @param config [dict] a key-value dict that contains all keyword in
    corresponding section of the config file
    @return [boolean] True if the open success, False otherwise
    """
    raise NotImplementedError("load")

  def open(self):
    """This function must be overloaded

    This function must open the database. Make here all
    needed operation to start your database. Error that must
    appear here are only relatives to database opening
    @return [boolean] True if the open success, False otherwise
    """
    raise NotImplementedError("open")

  def close(self):
    """This function must be overloaded

    This function must close/unload the database. Make here all operation
    that properly close the database
    """
    raise NotImplementedError("close")

  def getUserList(self):
    """Return the list of user from original storage

    Return the list of current user and their hostnames.
    @return [list] the list of User
            [None] if the database query fail
    """
    raise NotImplementedError("getUserList")

  def processUpdate(self, request):
    """Return the list of user from original storage

    @param request [Database.DbUpdate] the instance of update which contains
      all parameters field
    @return [bool] : the result of the operation
          True if update success
          False if not
    """
    raise NotImplementedError("processUpdate")

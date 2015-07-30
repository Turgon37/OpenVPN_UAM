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

"""Database - This is the main entry point to database

This program class is an accesser to several programs classes contains openvpn
uam's datas. It manages these datas and ensures their integrity. It also allows
the updating of these datas.
"""

# System imports
import logging

# Project imports
from .adapter import Adapter

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database')


class Database(object):
  """Build an instance of the model program class
  """

  # database status
  UNLOAD = -1
  CLOSE = 0
  OPEN = 1

  def __init__(self, confparser):
    """Constructor: Build a new database object
    """
    self.__cp = confparser
    self.__adapter = None
    self.__status = self.UNLOAD
    self.__l_user = None

  def __newAdapter(self):
    """Load a new instance of selected adapter and return it

    This function try to import and load a new adapter object from
    the name given in configuration file.
    @return [object] the new adapter instance
    """
    name = self.__cp.getDatabaseAdapter()
    adapter = None

    try:
      g_sys_log.debug('Loading database adapter for "' + name + '"')
      mod = __import__('OpenVPNUAM.adapter.' + name, fromlist=['Connector'])
      adapter = mod.Connector()
      # adapter class checking
      if not isinstance(adapter, Adapter):
        adapter = None
        raise Exception('Adapter "' + name + '" must extend Adapter class')
      if adapter.getName() != name:
        adapter = None
        raise Exception('Adapter name "' + adapter.getName() +
                        '" doesn\'t match with class name "' + name + '"')
    except ImportError as e:
      g_sys_log.error('Adapter "' + name +
                      '" cannot be found in adapter/ directory. ' + str(e))
    except Exception as e:
      g_sys_log.error('Adapter "' + name +
                      '" has encounter an error: ' + str(e))
    finally:
      return adapter

  def open(self):
    """Load the configured adapter as main database adapter

    Load the configured adapter and run open() on it to load the associated
    database
    @return [boolean] : a boolean indicates if the operation have succeded or
    not
    """
    if self.__adapter is None:
      self.__adapter = self.__newAdapter()

    adapter = self.__adapter
    if adapter is None:
      return False

    # adapter config checking
    if not self.__cp.has_section(adapter.getName()):
      g_sys_log.error('Configuration file require a section with name "' +
                      adapter.getName() + '"')
      return False

    try:
      # open database
      if adapter.open(self.__cp.getItemsFromSection(adapter.getName())):
        g_sys_log.debug('Opened database type "' + adapter.getName() + '"')
        self.__status = self.OPEN
        return True
      else:
        # loading error
        g_sys_log.error('Adapter "' + adapter.getName() +
                        '" failed to open database')
        return False
    except KeyError as e:
      g_sys_log.error('Adapter "' + adapter.getName() + '" require "' +
                      str(e) + ' missing parameters see adapter documentation')
      return False
    except Exception as e:
      g_sys_log.error('Adapter "' + adapter.getName() +
                      '" has encounter an error: ' + str(e))
      return False

  def close(self):
    """Load the configured adapter as main database adapter

    @return [boolean] : a boolean indicates if the operation have succeded or
    not
    """
    assert self.__status == self.OPEN
    if self.__adapter.close():
      self.__status = self.CLOSE

  def getUserList(self):
    """Call the adapter to return the current user list

    @return [list<User>] the current list of user
    """
    assert self.__adapter is not None
    assert self.__status == self.OPEN
    # TODO polling
    if self.__l_user is None:
      self.__l_user = self.__adapter.getUserList()

    return self.__l_user

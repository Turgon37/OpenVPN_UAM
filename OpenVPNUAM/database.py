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

This class aims to be a proxy between real data and main routine.
Real data are stored into some technology and are accessible by using specific
adapter. This class provide a little cache in case where the loaded adapter
where no longer to able to get us new data.
"""

# System imports
import logging
import time

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
    # this is the cached list of user
    self.__l_user = None
    # number of second from epoch at the last adapter polling
    self.__db_poll_ref = 0.0
    # number of second between two consecutive poll from adapter
    self.__db_poll_time = 600.0
    # number of second from epoch at the last adapter polling
    self.__db_poll_ref = 0.0
    # number of second between two consecutive poll from adapter
    self.__db_poll_time = 600.0
    
  def load(self):
    """Load parameter from config
    
    Check the input parameter to be sure they are valid
    @return [bool] True if parameter success, False otherwise
    """
    if not self.__cp.has_section(self.__cp.DATABASE_SECTION):
      return False
    if 'db_poll_time' not in self.__cp.getItems(self.__cp.DATABASE_SECTION):
      g_sys_log.debug('Use default database poll time of ' +
                      str(self.__db_poll_time))
    else:
      try:
        self.__db_poll_time = float(
            self.__cp.getItems(self.__cp.DATABASE_SECTION)['db_poll_time'])
      except ValueError as e:
        g_sys_log.error('Invalid format for "db_poll_time" option')
        return False
    if 'cert_poll_time' not in self.__cp.getItems(self.__cp.DATABASE_SECTION):
      g_sys_log.debug('Use default certificate poll time of ' +
                      str(self.__cert_poll_time))
    else:
      try:
        self.__cert_poll_time = float(
            self.__cp.getItems(self.__cp.DATABASE_SECTION)['cert_poll_time'])
      except ValueError as e:
        g_sys_log.error('Invalid format for "cert_poll_time" option')
        return False
        
    self.__status = self.CLOSE
    return True

  def __newAdapter(self):
    """Load a new instance of selected adapter and return it

    This function try to import and load a new adapter object from
    the name given in configuration file.
    @return [object] the new adapter instance
    """
    name = self.__cp.getItems(self.__cp.DATABASE_SECTION)['adapter']
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
    assert self.__status == self.CLOSE
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
      if adapter.open(self.__cp.getItems(adapter.getName())):
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
    assert self.__status == self.OPEN
    # refresh the internal cached list by ask again the adapter
    if time.time() - self.__db_poll_ref >= self.__db_poll_time:
      l_u = self.__adapter.getUserList()
      # error in data retrieving from DB
      if l_u is not None:
        self.__db_poll_ref = time.time()
        # set the reference to self into all user entities
        for user in l_u:
          user.setDb(self)
        self.__l_user = l_u

    return self.__l_user

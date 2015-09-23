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
from queue import Queue

# Project imports
from .adapter import Adapter

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database')


class DbUpdate(object):
  """This class represent a unique field update"""

  def __init__(self, field, value, obj):
    """This build a update request

    @param field [str] the name of the attribute to update
    @param value [mixed base type] the new value for the field above
    @param obj [object] the model instance to use as reference
      The update will be perform on this object, in local memory as first
      part, and then in remote database.
    """
    self.field = field
    self.new_value = value
    self.reference = obj


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
    # reference to the configparser use for retrieve configuration option
    self.__cp = confparser
    # this is the adapter instance to implement DB call
    self.__adapter = None
    # This status value inform about DATABASE status
    self.__status = self.UNLOAD
    # This is the list of User class
    # At the first query on this database, this list will be
    # filled with data present currently in database. Later if something
    # ask again the same query, the result will not be get from adapter
    # but from this attributes. This process implement a cache system for
    # data of this application
    self.__l_user = None
    # The database data are polled from adapter at a specific time interval
    # this interval is specified by theses following two values
    # number of second from epoch at the last adapter polling
    self.__db_poll_ref = 0.0
    # STATIC number of second between two consecutive poll from adapter
    self.__db_poll_time = 600.0
    # number of second to wait for database to be available on start
    # this value will not be use in this class but must be read from another
    # overclass
    self.__db_wait_time = 30
    # This queue store the list of update to perform in real database
    # Each item in this, must be send to the adapter for being incldue in
    # database backend. Note that while there is at least one item in this list
    # No database pull will be perform to prevent local database from update
    # lost
    self.__queue_update = Queue()

  def load(self):
    """Load parameter from config

    Check the input parameter to be sure they are valid
    @return [bool] True if parameter success, False otherwise
    """
    assert self.__status == self.UNLOAD
    if not self.__cp.has_section(self.__cp.DATABASE_SECTION):
      g_sys_log.error('Missing database section in configuration file')
      return False

    # try to load db_poll_time from configuration
    self.__db_poll_time = self.__cp.getfloat(self.__cp.DATABASE_SECTION,
                                             'db_poll_time',
                                             fallback=self.__db_poll_time)

    self.__db_wait_time = self.__cp.getfloat(self.__cp.DATABASE_SECTION,
                                             'db_wait_time',
                                             fallback=self.__db_wait_time)

    # instanciate a new Adapter object to be use during this session
    self.__adapter = self.__newAdapter()
    if self.__adapter is None:
      return False

    # adapter config checking
    if not self.__cp.has_section(self.__adapter.name):
      g_sys_log.error('Configuration file require a section with name "' +
                      self.__adapter.name + '"')
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

    g_sys_log.debug('Loading database adapter for "' + name + '"')
    try:
      mod = __import__('OpenVPNUAM.adapter.' + name, fromlist=['Connector'])
      adapter = mod.Connector()
    except ImportError as e:
      g_sys_log.error('Adapter "%s" cannot be found in adapter/ directory. %s',
                      name,
                      str(e))
      return None
    except AttributeError as e:
      g_sys_log.error('Adapter "%s" must use Connector as class name. %s',
                      name,
                      str(e))
      return None
    # adapter class checking
    if not isinstance(adapter, Adapter):
      g_sys_log.error('Adapter "%s" must extend Adapter class',
                      adapter.name)
      return None

    # adapter class name checking
    if adapter.name != name:
      g_sys_log.error('Adapter name "%s" doesn\'t match with class name %s',
                      adapter.name,
                      name)
      return None

    if not self.__cp.has_section(adapter.name):
      g_sys_log.error('Adapter "%s" required a configuration section with ' +
                      'the same name',
                      name)
      return None

    try:
      if not adapter.load(self.__cp.getItems(adapter.name)):
        return None
    except KeyError as e:
      g_sys_log.error('Adapter "%s" required a missing parameter. %s',
                      name,
                      str(e))
      return None
    return adapter

  def open(self):
    """Say to the adapter to open it database, and print debug message

    @return [bool] : a boolean indicates if the operation have succeded or
    not
    """
    if self.__openAdapter():
      g_sys_log.debug('Opened database type "%s"', self.__adapter.name)
      return True
    else:
      # loading error
      g_sys_log.error('Adapter "%s" failed to open database',
                      self.__adapter.name)
      return False

  def __openAdapter(self):
    """This function open the database adapter and handle only severe error

    @return [bool] : a boolean indicates if the operation have succeded or
    not
    """
    assert self.__status == self.CLOSE
    assert self.__adapter is not None

    try:
      # open database
      if self.__adapter.open():
        self.__status = self.OPEN
        return True
      else:
        return False
    except KeyError as e:
      g_sys_log.error('Adapter "%s" require %s missing parameters.' +
                      'See adapter documentation' +
                      self.__adapter.name +
                      str(e))
      return False
    except Exception as e:
      g_sys_log.error('Adapter "%s" has encounter an error: %s' +
                      self.__adapter.name +
                      str(e))
      return False

  def close(self):
    """Load the configured adapter as main database adapter

    @return [bool] : a boolean indicates if the operation have succeded or
    not
    """
    assert self.__status == self.OPEN
    # it's in charge of Adapter itself to properly close the database
    if self.__adapter.close():
      self.__status = self.CLOSE
    else:
      g_sys_log.error("Error during adapter closing")

# Getters methods
  @property
  def status(self):
    """Return status of this database
    """
    return self.__status

  @property
  def db_poll_time(self):
    """Return the time between two poll to database

    @return [int] The number of second from the next database polling
    """
    return self.__db_poll_time

  @property
  def db_wait_time(self):
    """Return the time between two poll to database

    @return [int] The number of second between the two consecutive
         attempt of database opening
    """
    return self.__db_wait_time

  def getUserList(self):
    """Call the adapter to return the current user list

    @return [list<User>] the current list of user
    """
    assert self.__status == self.OPEN
    # refresh the internal cached list by ask again the adapter
    if time.time() - self.__db_poll_ref >= self.__db_poll_time:
      g_sys_log.debug("=> Pull data from the adapter")
      l_u = self.__adapter.getUserList()
      # error in data retrieving from DB
      if l_u is not None:
        self.__db_poll_ref = time.time()
        # set the reference to self into all user entities
        self.__l_user = l_u
      else:
        g_sys_log.error("Unable to fetch data from adapter. Use local data")

    return self.__l_user

  def getEnabledUserList(self):
    """Return only the enabled user list

    @return [list<User>] the current list of enabled user(s)
    """
    enabled_user = []
    for user in self.getUserList():
      if user.is_enabled:
        enabled_user.append(user)
    return enabled_user

  def getDisabledUserList(self):
    """Return only the disabled user list

    @return [list<User>] the current list of disabled user(s)
    """
    disabled_user = []
    for user in self.getUserList():
      if not user.is_enabled:
        disabled_user.append(user)
    return disabled_user

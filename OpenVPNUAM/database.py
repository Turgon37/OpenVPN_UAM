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
import queue

# Project imports
from .adapters import Adapter

# Global project declarations
g_sys_log = logging.getLogger('openvpn-uam.database')


class DbRequest(object):
  """This class represent a unique field update

  An update query to database is first represented by an instance of this
  class
  """
  NO_CHANGE_CONSTRAINT = -1

  def __init__(self):
    self.__expected_change = self.NO_CHANGE_CONSTRAINT
    self.__last_update = None
    self.__error = False
    self.__error_msg = None

  @property
  def expected_change(self):
    """Get the expected number of rows

    @return [int] : the number of row expected
    """
    return self.__expected_change

  @property
  def is_error(self):
    """Return the error state of this update

    @return [bool] : the error status
    """
    return self.__error

  @property
  def error_msg(self):
    """Return the error explanation

    @return [str] : the error description if available
    """
    return self.__error_msg

# Setters
  @expected_change.setter
  def expected_change(self, num):
    """Set the expected number of rows

    @param num [int] : the number of row expected
    """
    self.__expected_change = num

  @is_error.setter
  def is_error(self, state):
    """Set the error state for this update

    @param state [bool] the new error state of this update
    """
    assert isinstance(state, bool)
    self.__error = state

  @error_msg.setter
  def error_msg(self, msg):
    """Set the error explanation

    @param msg [str] : the error description
    """
    assert isinstance(msg, str)
    self.__error_msg = msg

# API
  def update(self):
    """Update the time of the last adapter push
    """
    self.__last_update = time.time()

  def hasToBeUpdated(self):
    """Indicates if the current DbUpdate must be push to the adapter

    @return [bool] the 'toBeUpdatedStatus' of this update query
    """
    # if none => must be updated
    if self.__last_update is None:
      return True
    else:
      return (time.time() - self.__last_update) >= 30


class Database(object):
  """Build an instance of the model program class
  """

  # database status
  UNLOAD = -1
  CLOSE = 0
  OPEN = 1

# # INSTANCE OF UPDATE REQUEST
  class DbUpdate(DbRequest):

    def __init__(self, field, value, obj):
      """This build a update request

      @param field [str] the name of the attribute to update
      @param value [mixed base type] the new value for the field above
      @param obj [object] the model instance to use as reference
      """
      DbRequest.__init__(self)
      self.__field = field
      self.__value = value
      self.__reference = obj

# Getters
    @property
    def field(self):
      """Get the name of the field to update in target

      @return [str] : the name of the field to update
      """
      return self.__field

    @property
    def value(self):
      """Get the new value for the field 'field' in target

      @return [object] the new value for the field
      """
      return self.__value

    @property
    def target(self):
      """Get the reference to the object instance designed by the update

      @return [object] the target object
      """
      return self.__reference

    @property
    def target_type(self):
      """Get the name of class for object in reference with this update

      @return [str] : the name of the class
      """
      return type(self.target).__name__

# Tools
    def __str__(self):
      """Return a basic definition of this update query as string

      @return [str] a string that describe the update request
      """
      return (self.target_type +
              "(" + str(self.target.id) + ")" +
              "['" + self.field + "'] = " + str(self.value))
# # //INSTANCE OF UPDATE REQUEST

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
    self.__l_user = []
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
    # Each item in this, must be send to the adapter for being executed in
    # database backend. Note that, while there is at least one item in this
    # list no database pull will be perform to prevent local database from
    # update lost
    self.__queue_update = queue.Queue()
    self.__queue_error = queue.Queue()

  def load(self):
    """Load parameter from config

    Check the input parameter to be sure they are valid
    @return [bool] True if parameter success, False otherwise
    """
    assert self.__status == self.UNLOAD
    if not self.__cp.has_section(self.__cp.DATABASE_SECTION):
      g_sys_log.error("Missing '%s' section in configuration file",
                      self.__cp.DATABASE_SECTION)
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

    self.__status = self.CLOSE
    return True

  def __newAdapter(self):
    """Load a new instance of selected adapter and return it

    This function try to import and load a new adapter object from
    the name given in configuration file.
    @return [object] the new adapter instance
    """
    try:
      name = self.__cp.getItems(self.__cp.DATABASE_SECTION)['adapter']
    except KeyError:
      g_sys_log.fatal("Missing 'adapter' item in '%s' section of configuration",
                      self.__cp.DATABASE_SECTION)
      return False
    adapter = None

    g_sys_log.debug("Loading database adapter with name '%s'", name)
    try:
      mod = __import__('OpenVPNUAM.adapters.' + name, fromlist=['Connector'])
      adapter = mod.Connector()
    except ImportError as e:
      g_sys_log.fatal("Adapter '%s' cannot be found in adapters/ directory. %s",
                      name,
                      str(e))
      return None
    except AttributeError as e:
      g_sys_log.fatal("Adapter '%s' must use Connector as class name. %s",
                      name,
                      str(e))
      return None
    except Exception as e:
      g_sys_log.fatal("Adapter '%s' failed to be load. %s", name, str(e))
      return None

    # adapter class checking
    if not isinstance(adapter, Adapter):
      g_sys_log.fatal("Adapter '%s' must extend Adapter class", name)
      return None

    # adapter class name checking
    if adapter.name != name:
      g_sys_log.error("Adapter name '%s' doesn't match with class name %s",
                      adapter.name, name)
      return None

    if not self.__cp.has_section(adapter.name):
      g_sys_log.error("Adapter '%s' required a configuration section with " +
                      "the same name", name)
      return None

    try:
      if not adapter.load(self.__cp.getItems(adapter.name)):
        return None
    except KeyError as e:
      g_sys_log.error("Adapter '%s' required a missing parameter. %s",
                      name, str(e))
      return None
    g_sys_log.info("Using database adapter '%s'", name)
    return adapter

  def open(self):
    """Say to the adapter to open it database, and print debug message

    @return [bool] : a boolean indicates if the operation have succeded or
    not
    """
    assert self.__status == self.CLOSE

    if self.__openAdapter():
      self.__status = self.OPEN
      g_sys_log.debug("Opened database type '%s'", self.__adapter.name)
      return True
    else:
      # loading error
      g_sys_log.error("Adapter '%s' failed to open database",
                      self.__adapter.name)
      return False

  def __openAdapter(self):
    """This function open the database adapter and handle only severe error

    @return [bool] : a boolean indicates if the operation have succeded or
    not
    """
    assert self.__adapter is not None

    try:
      # open database
      if self.__adapter.open():
        return True
      else:
        return False
    except KeyError as e:
      g_sys_log.error("Adapter '%s' require '%s' missing parameters. " +
                      "See adapter documentation",
                      self.__adapter.name,
                      str(e))
      return False
    except Exception as e:
      g_sys_log.error("Adapter '%s' has encounter an error: %s",
                      self.__adapter.name,
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
      g_sys_log.error('Error during adapter closing')

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

  def __getUserListFromAdapter(self):
    """Call the adapter to retrieve user list from its associated storage

    @return [list<User>] : the list of user given from adapter
    """
    l = self.__adapter.getUserList()
    if l is not None:
      for row in l:
        row.db = self
    return l

  def api(func):
    """Decorator for all API functions

    Apply this decorator to all functions that belong to the external API
    """
    def backgroundTask(self, *args, **kwargs):
      """Execute background tasks for databases

      This function makes some background tasks for the database :
        * check data's cache validity
        * process update on required
      """
      assert self.__status == self.OPEN

      # CHECK DATA CACHE VALIDITY
      # refresh the internal cached list by ask again the adapter
      # csheck if the last poll have been realized from sufficient amount
      # of time
      if ((time.time() - self.__db_poll_ref >= self.__db_poll_time) and
         self.__queue_update.empty()):
        g_sys_log.debug("=> Pull data from the adapter")
        l_u = self.__getUserListFromAdapter()
        # error in data retrieving from DB
        if l_u is not None:
          self.__db_poll_ref = time.time()
          # set the reference to self into all user entities
          self.__l_user = l_u
        else:
          g_sys_log.error("Unable to fetch data from adapter. Use local data")

      self.__processUpdate()
      return func(self, *args, **kwargs)
    return backgroundTask

  def __processUpdate(self):
    """Treat all update request which are pending into the queue
    """
    for i in range(self.__queue_update.qsize()):
      try:
        up = self.__queue_update.get_nowait()
      except queue.Empty:
        return

      # if it is not the time for the update to be performed
      if not up.hasToBeUpdated():
        self.__queue_update.put_nowait(up)
      else:
        # if update failed into adapter
        up.update()
        if not self.__adapter.processUpdate(up):
          # an error mean the update has been performed but incorrectly
          if up.is_error:
            g_sys_log.error("Error during update query : " + str(up))
            # push the update query into error queue
            self.__queue_error.put(up)
          # no error means that the update has not been performed
          else:
            g_sys_log.error("Error with adapter during update query : " + str(up))
            # push the update query into error queue
            self.__queue_update.put_nowait(up)

# API DATABASE
  @api
  def getUserList(self):
    """Call the adapter to return the current user list

    @return [list<User>] the current list of user
    """
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

  def update(self, field, value, obj, count=DbUpdate.NO_CHANGE_CONSTRAINT):
    """Queue a new update request

    Attempt to update a field identified by 'field' string with the value
    in 'value' parameter. This update will be applyed to object passed as
    parameter. This function call the adapter to perform an update
    of the key identified by 'field' argument for the current user with the
    new value given in 'value' argument.
    @param field [str] : the name of the current user's attribute to update
    @param value [MIX] : the new value for the 'field' named attribute
    @param obj [MIX] : the object to pass to adapter for running the update
    """
    update = Database.DbUpdate(field, value, obj)
    update.expected_change = count
    self.__queue_update.put(update)
    self.__processUpdate()
